import requests
import sendgrid
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.db.models import Count, Q
from django.utils.text import slugify
from requests.auth import HTTPBasicAuth
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import is_server_error
from rest_framework.views import APIView

from corcym import settings
from corcym.settings import (
    COMMUNICATION,
    COUSTOMER_QUALITY,
    DEFAULT_FROM_EMAIL,
    DONATION_EMAIL,
    PATH_P,
    SENDGRID_API_KEY,
)
from support.email_pdf import genrate_email_pdf
from support.models import (
    Donation,
    EmailSupport,
    HowCanWeHelpYou,
    IAm,
    query_donation_email_by_args,
    query_support_email_by_args,
)
from support.serializers import (
    DonationCountrySerializer,
    DonationEmailSerializer,
    EmailCitySerializer,
    EmailCountrySerializer,
    EmailSerializer,
    HowCanWeHelpYouSerializer,
    TypeRequestSerializer,
    WhoIAmViewSerializer,
)

sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
import datetime
from io import BytesIO

import boto3
import PyPDF2
from botocore.exceptions import NoCredentialsError

from corcym.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
)
from support.donation_pdf import genrate_donation_pdf


# structurel api
class BaseAPIView(APIView):
    authentication_classes = ()
    permission_classes = (IsAuthenticated,)

    def send_response(
        self,
        success=False,
        code="",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        payload={},
        description="",
        exception=None,
        count=0,
        log_description="",
    ):
        if not success and is_server_error(status_code):
            if settings.DEBUG:
                description = f"error message: {description}"
            else:
                description = "Internal server error."
        return Response(
            data={
                "success": success,
                "code": code,
                "payload": payload,
                "description": description,
                "count": count,
            },
            status=status_code,
        )

    def message(self, data):
        body = f"""
		First Name: {data['first_name']}
		Last Name: {data['last_name']}
		Message: {data['message']}
		City: {data['city']}
		I Am: {data['i_am']}
		Email:{data['email']}
		State:{data['state']}
		Phone Number:{data['phone_number']}
		how_can_we_help:{data['how_can_we_help']}
		"""
        return body

    @staticmethod
    def get_oauth_token(email="", password="", grant_type="password"):
        try:
            url = settings.AUTHORIZATION_SERVER_URL
            print(url)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            print(headers)
            data = {"username": email, "password": password, "grant_type": grant_type}
            print(data)
            auth = HTTPBasicAuth(settings.OAUTH_CLIENT_ID, settings.OAUTH_CLIENT_SECRET)
            print("auth")
            response = requests.post(url=url, headers=headers, data=data, auth=auth)
            print(response)
            print(response.ok)
            if response.ok:
                json_response = response.json()
                return {
                    "access_token": json_response.get("access_token", ""),
                    "refresh_token": json_response.get("refresh_token", ""),
                }
            else:
                return {"error": response.json().get("error")}
        except Exception as e:
            print(e)
            return {"exception": str(e)}

    @staticmethod
    def revoke_oauth_token(token):
        try:
            url = settings.REVOKE_TOKEN_URL
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "token": token,
                "client_secret": settings.OAUTH_CLIENT_SECRET,
                "client_id": settings.OAUTH_CLIENT_ID,
            }
            response = requests.post(url=url, headers=headers, data=data)
            if response.ok:
                return True
            else:
                return False
        except Exception:
            # fixme: Add logger to log this exception
            return False


# post and get support email
class EmailSendingView(BaseAPIView):
    permission_classes = (AllowAny,)

    def upload_to_aws(self, local_file, bucket, s3_file):
        s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        try:
            a = s3.upload_file(local_file, bucket, s3_file)
            print("Upload Successful", a)
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False
        except s3.exceptions:
            print("known error occured")
        except ClientError as e:
            print("Unexpected error: %s" % e)

    def send_mail(self, template_id, sender, recipient, data_dict):
        try:
            message = sendgrid.helpers.mail.Mail(
                from_email=sender, to_emails=recipient, subject=""
            )
            message.dynamic_template_data = data_dict
            message.template_id = template_id
            status = sg.send(message)
            # response = sg.client.mail.send.post(request_body=mail.get())
            print(status)
        except Exception as e:
            print("INSIDE")
            return e

    def get(self, request, pk=None):
        try:
            if pk is not None:
                data = EmailSupport.objects.get(id=pk)
                serializer = EmailSerializer(data)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Support Email",
                    log_description="",
                )
            data = EmailSupport.objects.all()
            serializer = EmailSerializer(data, many=True)
            print(serializer.data)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Support Email",
                log_description="",
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Support Email doesn't exsist.",
            )
        except EmailSupport.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Support Email doesn't exsist.",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)

    def post(self, request):
        try:
            data = request.data
            pdf_data = data
            serializer = EmailSerializer(data=data)
            if serializer.is_valid():
                booking_saved = serializer.save()
                data = serializer.data

                template_id = "d-96000e92b8c4429da16464a5e32aac3a"
                user_template = "d-b2fba4789d984e89832e2e47b8232364"

                pdf_data["how_can_we_help"] = data["how_can_we_help"]
                pdf_data["i_am"] = data["i_am"]
                path = f"{PATH_P}support_email_{pdf_data['first_name']}.pdf"

                genrate_email_pdf(pdf_data, path)
                a = self.upload_to_aws(
                    local_file=path,
                    bucket="corcym",
                    s3_file=f"uploads/support_email_{pdf_data['first_name']}.pdf",
                )
                file_link = f"https://corcym.s3.amazonaws.com/uploads/support_email_{pdf_data['first_name']}.pdf"
                data_dict = {"link": file_link}
                if (
                    data["how_can_we_help"] == "Product feedback"
                    or data["how_can_we_help"] == " Report a problem with our devices"
                    or data["how_can_we_help"] == "Patient card and registration form"
                    or data["how_can_we_help"] == "Collaborate with us"
                ):
                    res = self.send_mail(
                        template_id, DEFAULT_FROM_EMAIL, COUSTOMER_QUALITY, data_dict
                    )
                    self.send_mail(
                        user_template, DEFAULT_FROM_EMAIL, [data["email"]], data_dict
                    )
                    return self.send_response(
                        success=True,
                        code=f"201",
                        status_code=status.HTTP_201_CREATED,
                        description="Email sent to customerquality@corcym.com",
                    )
                res = self.send_mail(
                    template_id, DEFAULT_FROM_EMAIL, COMMUNICATION, data_dict
                )
                self.send_mail(
                    user_template, DEFAULT_FROM_EMAIL, [data["email"]], data_dict
                )
                print(res)
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Email sent to communication@corcym.com",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except EmailSupport.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Booking doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


# get details and post donation email
class DonationEmailSendingView(BaseAPIView):
    permission_classes = (AllowAny,)

    def upload_to_aws(self, local_file, bucket, s3_file):
        s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        try:
            a = s3.upload_file(local_file, bucket, s3_file)
            print("Upload Successful", a)
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False
        except s3.exceptions:
            print("known error occured")
        except ClientError as e:
            print("Unexpected error: %s" % e)

    def concat_pdf(self, path1, path2, data, time):
        pdf1File = path1
        pdf1Reader = PyPDF2.PdfFileReader(pdf1File)
        pdf2Reader = path2
        pdfWriter = PyPDF2.PdfFileWriter()
        for pageNum in range(pdf1Reader.numPages):
            pageObj = pdf1Reader.getPage(pageNum)
            pdfWriter.addPage(pageObj)
        for pageNum in range(pdf2Reader.numPages):
            pageObj = pdf2Reader.getPage(pageNum)
            pdfWriter.addPage(pageObj)

        pdfOutputFile = open(
            f"{PATH_P}{time}_{slugify(data['name'])}_donation2pdf.pdf", "wb"
        )
        pdfWriter.write(pdfOutputFile)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                data = Donation.objects.get(id=pk)
                serializer = DonationEmailSerializer(data)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Donation Email",
                    log_description="",
                )
            data = Donation.objects.all()
            serializer = DonationEmailSerializer(data, many=True)
            print(serializer.data)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Donation Email",
                log_description="",
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Donation Email doesn't exsist.",
            )
        except Donation.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Donation Email doesn't exsist.",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)

    def send_mail(self, template_id, sender, recipient, data_dict):
        try:
            message = sendgrid.helpers.mail.Mail(
                from_email=sender, to_emails=recipient, subject=""
            )
            message.dynamic_template_data = data_dict
            message.template_id = template_id
            status = sg.send(message)
            # response = sg.client.mail.send.post(request_body=mail.get())
            print(status)
        except Exception as e:
            print("INSIDE")
            return e

    def post(self, request):
        try:
            data = request.data
            pdf_data = data
            print(pdf_data)
            serializer = DonationEmailSerializer(data=data)
            if serializer.is_valid():
                booking_saved = serializer.save()
                data = serializer.data
                print(data)
                template_id = "d-4fff1b4ae03544c899f759350aa2d131"
                data_dict = {}
                time = datetime.datetime.now().strftime("%d_%b_%Y")
                path = f"{PATH_P}{time}_donation_email_{slugify(pdf_data['name'])}.pdf"
                genrate_donation_pdf(pdf_data, path)
                print("-------------1----------------")
                s3 = boto3.resource(
                    "s3",
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                )

                bucket = s3.Bucket("corcym")
                upload = bucket.objects.filter(Prefix="uploads")
                for each in upload:
                    if each.key == serializer.instance.w9_form:
                        fs = each.get()["Body"].read()
                        pdfFile = PyPDF2.PdfFileReader(BytesIO(fs))
                        self.concat_pdf(path1=path, path2=pdfFile, data=data, time=time)

                s3_file_path = (
                    f"uploads/{time}_{slugify(data['name'])}_donation2pdf.pdf"
                )
                a = self.upload_to_aws(
                    local_file=f"{PATH_P}{time}_{slugify(data['name'])}_donation2pdf.pdf",
                    bucket="corcym",
                    s3_file=s3_file_path,
                )
                file_link = f"https://corcym.s3.amazonaws.com/{s3_file_path}"
                data_dict = {"link": file_link}
                res = self.send_mail(
                    template_id, DEFAULT_FROM_EMAIL, DONATION_EMAIL, data_dict
                )
                # print(res)
                user_template = "d-b2fba4789d984e89832e2e47b8232364"
                data = serializer.data
                res = self.send_mail(
                    user_template, DEFAULT_FROM_EMAIL, [data["email"]], data_dict
                )
                print(res)
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Donation email is created",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except Donation.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Donation doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


# get details and post donation email
class WhoIAmView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                iam = IAm.objects.get(id=pk)
                serializer = WhoIAmViewSerializer(iam)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Who I am",
                    log_description="",
                )
            iam = IAm.objects.all()
            serializer = WhoIAmViewSerializer(iam, many=True)
            print(serializer.data)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Who I am",
                log_description="",
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Who I am data exsist.",
            )
        except IAm.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Who I am doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


# How can we help you constant
class HowCanIHelpYouView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                data = HowCanWeHelpYou.objects.get(id=pk)
                serializer = HowCanWeHelpYouSerializer(data)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="How can we help  you",
                    log_description="",
                )
            data = HowCanWeHelpYou.objects.all()
            serializer = HowCanWeHelpYouSerializer(data, many=True)
            print(serializer.data)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="How can we help  you",
                log_description="",
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No How can we help  you data exsist.",
            )
        except HowCanWeHelpYou.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="How can we help  you doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


# Data table of email view
class EmailViewSet(viewsets.ModelViewSet, BaseAPIView):
    permission_classes = (AllowAny,)
    queryset = EmailSupport.objects.all()
    serializer_class = EmailSerializer

    def list(self, request, **kwargs):
        try:
            country = request.query_params.get("country", None)
            how_can_we_help = request.query_params.get("how_can_we_help", None)
            i_am = request.query_params.get("i_am", None)
            query_object = Q()
            print(query_object)

            if country:
                query_object &= Q(country=country)

            if how_can_we_help:
                query_object &= Q(how_can_we_help__name=how_can_we_help)

            if i_am:
                query_object &= Q(i_am__title=i_am)

            print(query_object)

            email = query_support_email_by_args(query_object, **request.query_params)

            serializer = EmailSerializer(email["items"], many=True)

            result = dict()
            result["data"] = serializer.data
            result["draw"] = email["draw"]
            result["recordsTotal"] = email["total"]
            result["recordsFiltered"] = email["count"]
            print("restlt:  \n", result)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=result,
                code="200",
                description="Support Email Details",
                log_description="",
            )
        except EmailSupport.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Support Email doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


# data table view of donation
class DonationViewSet(viewsets.ModelViewSet, BaseAPIView):
    permission_classes = (AllowAny,)
    queryset = Donation.objects.all()
    serializer_class = DonationEmailSerializer

    def list(self, request, **kwargs):
        try:

            TYPE_OF_REQUEST = {
                "Educational Grant": 1,
                "Research Grant": 2,
                "Third party educational events": 3,
                "Charitable Donation": 4,
            }
            type_of_request = request.query_params.get("type_of_request", "")
            country = request.query_params.get("country", "")
            print(country)
            query_object = Q()
            if country != "":
                query_object &= Q(country=country)
            if type_of_request != "":
                query_object &= Q(type_of_request=TYPE_OF_REQUEST[type_of_request])

            donation = query_donation_email_by_args(
                query_object, **request.query_params
            )

            serializer = DonationEmailSerializer(donation["items"], many=True)

            result = dict()
            result["data"] = serializer.data
            result["draw"] = donation["draw"]
            result["recordsTotal"] = donation["total"]
            result["recordsFiltered"] = donation["count"]
            print("restlt:  \n", result)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=result,
                code="200",
                description="Donation email Details",
                log_description="",
            )
        except Donation.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Donation email doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


# Get countries of eamil view
class EmailCountryView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            country = (
                EmailSupport.objects.values("country")
                .annotate(dcount=Count("country"))
                .order_by()
            )
            print(country)
            serializer = EmailCountrySerializer(country, many=True)
            print(serializer.data)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
            )
        except EmailSupport.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="EmailSupport doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print("Exception: ", e)
            return self.send_response(code=f"500", description=e)


# get the group of emails city by id
class EmailCityView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            city = (
                EmailSupport.objects.values("city")
                .annotate(dcount=Count("city"))
                .order_by()
            )
            print(city)
            serializer = EmailCitySerializer(city, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
            )
        except EmailSupport.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="EmailSupport doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print("Exception: ", e)
            return self.send_response(code=f"500", description=e)


# get support view of group by
class SupportGroupByView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            country = (
                EmailSupport.objects.values("country")
                .annotate(dcount=Count("country"))
                .order_by()
                .all()
            )
            how_can_we_help = (
                EmailSupport.objects.values("how_can_we_help")
                .annotate(dcount=Count("how_can_we_help"))
                .order_by()
                .all()
            )
            serializer = EmailCountrySerializer(country, many=True)
            howweserializer = WhoIAmViewSerializer(how_can_we_help, many=True)
            city = (
                EmailSupport.objects.values("city")
                .annotate(dcount=Count("city"))
                .order_by()
            )
            city_serializer = EmailCitySerializer(city, many=True)
            data = {
                "country": serializer.data,
                "how_can_we_help": howweserializer.data,
                "city": city_serializer.data,
            }
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=data,
                code="",
                description="Details of serializer",
                log_description="",
            )
        except EmailSupport.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Email Support doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print("Exception: ", e)
            return self.send_response(code=f"500", description=e)


# donation group by view
class DonationGroupByView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            country = (
                Donation.objects.values("country")
                .annotate(dcount=Count("country"))
                .order_by()
                .all()
            )
            type_of_request = (
                Donation.objects.values("type_of_request")
                .annotate(dcount=Count("type_of_request"))
                .order_by()
                .all()
            )
            serializer = DonationCountrySerializer(country, many=True)
            typeserializer = TypeRequestSerializer(type_of_request, many=True)
            data = {"country": serializer.data, "type_of_request": typeserializer.data}
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=data,
                code="",
                description="Details of serializer",
                log_description="",
            )
        except Donation.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Donation doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print("Exception: ", e)
            return self.send_response(code=f"500", description=e)
