import boto3
import sendgrid
from botocore.exceptions import ClientError, ParamValidationError
from django.core.exceptions import FieldError
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from sendgrid.helpers.mail import Email, Mail, Personalization

from contact.models import (
    Contact,
    InterestIn,
    IWouldLikeTo,
    Specialty,
    query_contact_by_args,
)
from contact.pdf_temp import genrate_contact_pdf
from contact.serializers import (
    ContactSerializers,
    InterestInSerializers,
    IWouldLikeSerializers,
    SpecialtySerializers,
)
from corcym.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
    CC_EMAILS,
    CONTACT_EMAILS,
    DEFAULT_FROM_EMAIL,
    EUA_COUNTRIES,
    LATAM_COUNTRIES,
    MECA_COUNTRIES,
    OTHER_COUNTRIES_CONTACT_EMAIL,
    PATH_P,
    SENDGRID_API_KEY,
)
from support.views import BaseAPIView

sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)


# Create your views here.
class ContactView(BaseAPIView):
    permission_classes = (AllowAny,)

    def send_mail(self, template_id, sender, recipient, cc_email, data_dict):
        try:
            message = sendgrid.helpers.mail.Mail(
                from_email=sender, to_emails=recipient, subject=""
            )
            message.dynamic_template_data = data_dict
            message.template_id = template_id
            if cc_email:
                p = Personalization()
                p.add_to(Email(recipient))
                for each in cc_email:
                    p.add_cc(Email(each))
                message.add_personalization(p)
                status = sg.send(message)
            else:
                status = sg.send(message)
            print(status)
            return True
        except Exception as e:
            return e

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

    def get(self, request, pk=None):
        try:
            if pk is not None:
                contact = Contact.objects.get(id=pk)
                serializer = ContactSerializers(contact)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of contact",
                    log_description="",
                )
            contacts = Contact.objects.all()
            serializer = ContactSerializers(contacts, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
            )
        except Contact.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Contact doesn't exists",
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
            serializer = ContactSerializers(data=data)
            if serializer.is_valid():
                ContactSaved = serializer.save()
                path = f"{PATH_P}contact_form{serializer.data['name']}.pdf"
                genrate_contact_pdf(serializer.data, path)
                cc_mail = None
                data_dict = {}
                a = self.upload_to_aws(
                    local_file=path,
                    bucket="corcym",
                    s3_file=f"upload/contact_form{serializer.data['name']}.pdf",
                )
                user_temp = "d-c1009726479a43ceab764437b55cbe78"
                mail_res = self.send_mail(
                    user_temp,
                    DEFAULT_FROM_EMAIL,
                    [serializer.data["email"]],
                    cc_mail,
                    data_dict,
                )
                data_dict = {
                    "link": f"https://corcym.s3.eu-central-1.amazonaws.com/uploads/contact_form{serializer.data['name']}.pdf"
                }
                admin_temp = "d-0520c2f0257a4738815c3b3ebcd95b5a"
                if (
                    serializer.data["country"].lower() in LATAM_COUNTRIES
                    and serializer.data["country"].lower() in MECA_COUNTRIES
                ):
                    email = CONTACT_EMAILS["Latam"] + CONTACT_EMAILS["MECA"]
                    email = list(set(email))
                    mail_res = self.send_mail(
                        admin_temp, str(DEFAULT_FROM_EMAIL), email, CC_EMAILS, data_dict
                    )
                elif (
                    serializer.data["country"].lower()
                    in str(CONTACT_EMAILS.keys()).lower()
                    and serializer.data["country"].lower() in MECA_COUNTRIES
                ):
                    email = (
                        CONTACT_EMAILS[serializer.data["country"]]
                        + CONTACT_EMAILS["MECA"]
                    )
                    email = list(set(email))
                    mail_res = self.send_mail(
                        admin_temp, str(DEFAULT_FROM_EMAIL), email, CC_EMAILS, data_dict
                    )
                elif (
                    serializer.data["country"].lower()
                    in str(CONTACT_EMAILS.keys()).lower()
                ):
                    mail_res = self.send_mail(
                        admin_temp,
                        str(DEFAULT_FROM_EMAIL),
                        CONTACT_EMAILS["country"],
                        CC_EMAILS,
                        data_dict,
                    )
                elif (
                    serializer.data["country"].lower() == "spain"
                    or serializer.data["country"].lower() == "portugal"
                ):
                    print("elif")
                    mail_res = self.send_mail(
                        admin_temp,
                        str(DEFAULT_FROM_EMAIL),
                        CC_EMAILS,
                        cc_mail,
                        data_dict,
                    )
                elif serializer.data["country"].lower() in LATAM_COUNTRIES:
                    mail_res = self.send_mail(
                        admin_temp,
                        str(DEFAULT_FROM_EMAIL),
                        CONTACT_EMAILS["Latam"],
                        CC_EMAILS,
                        data_dict,
                    )
                elif serializer.data["country"].lower() in EUA_COUNTRIES:
                    mail_res = self.send_mail(
                        admin_temp,
                        str(DEFAULT_FROM_EMAIL),
                        CONTACT_EMAILS["EUA"],
                        CC_EMAILS,
                        data_dict,
                    )
                elif serializer.data["country"].lower() in MECA_COUNTRIES:
                    mail_res = self.send_mail(
                        admin_temp,
                        str(DEFAULT_FROM_EMAIL),
                        CONTACT_EMAILS["MECA"],
                        CC_EMAILS,
                        data_dict,
                    )
                else:
                    print("else")
                    print(OTHER_COUNTRIES_CONTACT_EMAIL)
                    mail_res = self.send_mail(
                        admin_temp,
                        str(DEFAULT_FROM_EMAIL),
                        OTHER_COUNTRIES_CONTACT_EMAIL,
                        CC_EMAILS,
                        data_dict,
                    )
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="contact is created",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except Contact.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Contact doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class IWouldView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            i_would_like = IWouldLikeTo.objects.all()
            serializer = IWouldLikeSerializers(i_would_like, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
            )
        except IWouldLikeTo.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="I would Like To doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


class SpecialtyView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            specialty = Specialty.objects.all()
            serializer = SpecialtySerializers(specialty, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
            )
        except Specialty.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="I would Like To doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


class InterestInView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            intrestin = InterestIn.objects.all()
            serializer = InterestInSerializers(intrestin, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
            )
        except InterestIn.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="I would Like To doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


class ContactViewSet(viewsets.ModelViewSet, BaseAPIView):
    permission_classes = (AllowAny,)
    queryset = Contact.objects.all()
    serializer_class = ContactSerializers

    def boolean(self, status):
        if status == "true" or status == "True":
            return True
        else:
            return False

    def list(self, request, **kwargs):
        try:
            webinars_reg = query_contact_by_args(query_object, **request.query_params)
            if not webinars_reg:
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload={},
                    code="",
                    description="query_webinars_by_args Functions returning None",
                    log_description="",
                )

            serializer = ContactSerializers(webinars_reg["items"], many=True)

            result = dict()
            result["data"] = serializer.data
            result["draw"] = webinars_reg["draw"]
            result["recordsTotal"] = webinars_reg["total"]
            result["recordsFiltered"] = webinars_reg["count"]
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=result,
                code="",
                description="Details of webinars",
                log_description="",
            )
        except Contact.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Job doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)
