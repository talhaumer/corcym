from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.status import is_server_error
from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist
from corcym import settings
from requests.auth import HTTPBasicAuth
import requests
from support.views import BaseAPIView
from career.models import JobPosting, CandidateDetail, query_jobs_by_args, query_candidate_by_args, EmailData
from career.serializers import CandidateNewFieldSerializer, JobCityListingSerializer, CandidateJobSerializer, JobTitleSerializer, JobLocationSerializer, CandidateDetailSerializer, JobPostingSerializer, EmailDataSerializer, JobListingSerializer
from django.db.models import Q
import sendgrid
from sendgrid.helpers.mail import (Mail, Email,Personalization)
from corcym.settings import DEFAULT_FROM_EMAIL, SENDGRID_API_KEY, ADMIN_CAREER
sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
import time
from django.db.models import Count
from fpdf import FPDF
import PyPDF2
import boto3
from botocore.exceptions import NoCredentialsError
from corcym.settings import AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, PATH_P
from io import BytesIO
from rest_framework.parsers import FileUploadParser
from botocore.exceptions import ClientError, ParamValidationError
import pdfkit
from io import BytesIO
from django.template.loader import get_template
from django.http import HttpResponse
# from career.utils import render_to_pdf
from career.pdf_temp import genrate_pdf
# Create your views here.



class CandidateDetailView(BaseAPIView, FPDF):
	permission_classes = (AllowAny, )
	# parser_classes = (FileUploadParser,)
	
	def upload_to_aws(self, local_file, bucket, s3_file):
		s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
			aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
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


	def concat_pdf(self, path1, path2, data):
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

		pdfOutputFile = open(f"{PATH_P}{data['applicant_name']}sresume.pdf", 'wb')
		pdfWriter.write(pdfOutputFile)

	def send_mail(self, template_id, sender, recipient, data_dict):
		try:
			message = sendgrid.helpers.mail.Mail(
				from_email=sender,
				to_emails=recipient,
				subject=''
			)
			message.dynamic_template_data = data_dict
			message.template_id = template_id
			status = sg.send(message)
			return status
			return status
		except Exception as e:
			return e


	def get(self, request, pk=None):
		try:
			if pk is not None:
				job = JobPosting.objects.get(id=pk, status = True, deleted = False)
				serializer = JobPostingSerializer(job)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of job',log_description='')
			jobs = JobPosting.objects.filter(status = True, deleted = False)
			serializer = JobPostingSerializer(jobs, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except JobPosting.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Job doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print("Exception: ", e)
			return self.send_response(code=f'500',description=e)


	def post(self, request):
		try:
			data = request.data
			print(data)
			serializer = CandidateDetailSerializer(data= data)
			if serializer.is_valid():
				CandidateDetailSaved = serializer.save()
				templates = {'admin':'d-a0e4337ce6864cdd8c11a6be5b0a2f68',
				'candidate':'d-b763d599c2e6411897d779255f518197'}
				data_dict = {
				'jobLink':"https://corcym.com/detail-job/{}".format(serializer.data['job_id']),
				'job_title' : serializer.instance.job.job_title,
				'applicant_name' :serializer.data['first_name'],
				'applicant_Last_name' : serializer.data['last_name'],
				'cv' : f'https://corcym.s3.amazonaws.com/{serializer.instance.resume}'
				}

				
				s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
					aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

				bucket = s3.Bucket('corcym')
				upload = bucket.objects.filter(Prefix='uploads')
				for each in upload:
					if each.key == serializer.instance.resume:
						fs = each.get()['Body'].read()
						pdfFile = PyPDF2.PdfFileReader(BytesIO(fs))
				
				PATH = f'{PATH_P}{data_dict["applicant_name"]}s_request.pdf'
				data['job_title'] = serializer.instance.job.job_title,
				print(PATH)
				genrate_pdf(data, PATH)
				self.concat_pdf(path1=PATH, path2 = pdfFile, data = data_dict)
				a = self.upload_to_aws(local_file =f"{PATH_P}{data_dict['applicant_name']}sresume.pdf",bucket = 'corcym', s3_file = f"uploads/{data_dict['applicant_name']}sresume.pdf")
				data_dict['jobLink'] = f"https://corcym.s3.eu-central-1.amazonaws.com/uploads/{data_dict['applicant_name']}sresume.pdf"
				mail_res = self.send_mail(templates['admin'], DEFAULT_FROM_EMAIL,  ADMIN_CAREER,  data_dict)
				mail_res2 = self.send_mail(templates['candidate'], DEFAULT_FROM_EMAIL,  [serializer.data['email']], data_dict= {})
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
					payload = {
						"admin_resp" : str(mail_res),
						"candidate_resp" : str(mail_res2)
					},
					description='You applied for mentioned job sucessfuly')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except CandidateDetail.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Job doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print("Exception : ", e)
			return self.send_response(code=f'500',description=e)



class JobPostingView(BaseAPIView):
	permission_classes = (AllowAny, )
	def get(self, request, pk=None):
		try:
			if pk is not None:
				job = JobPosting.objects.get(id=pk, status = True, deleted = False)
				serializer = JobPostingSerializer(job)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of job',log_description='')
			jobs = JobPosting.objects.filter(status = True, deleted = False)
			serializer = JobPostingSerializer(jobs, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except JobPosting.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Job doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


	def post(self, request):
		try:
			data = request.data
			serializer = JobPostingSerializer(data= data)
			if serializer.is_valid():
				JobPostingSaved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Job is created')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except JobPosting.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Job doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


	def put(self, request, pk=None):
		try:
			id = pk
			saved_jobs = JobPosting.objects.get(id=id, status = True, deleted = False)
			data = request.data
			serializer = JobPostingSerializer(instance=saved_jobs, data=data, partial=True)
			if serializer.is_valid():
				JobPostingSaved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Job is updated')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No job matches the given query.")
		except JobPosting.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="job doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


class DeleteJobView(BaseAPIView):
	permission_classes = (AllowAny, )
	def get(self, request, pk=None):
		try:
			if pk is not None:
				job = JobPosting.objects.get(id=pk, deleted = False)
				job.status = not job.status
				job.save()
				if job.status == False:
					return self.send_response(description= "Job disabled successfuly",success=True,status_code=status.HTTP_200_OK, code='200')
				return self.send_response(description= "Job enabled successfuly",success=True,status_code=status.HTTP_200_OK, code='200')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description='id not found ')
		except JobPosting.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Job doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print(e)
			return self.send_response(code=f'500',description=e)


class AdminCandidateView(BaseAPIView):
	permission_classes = (AllowAny, )
	def get(self, request, pk=None):
		try:
			if pk is not None:
				candidate = CandidateDetail.objects.get(id=pk)
				serializer = CandidateDetailSerializer(candidate)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of candidate',log_description='')
			candidate = CandidateDetail.objects.all()
			print(candidate)
			serializer = CandidateDetailSerializer(candidate, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of candidate',log_description='')
		except CandidateDetail.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="candidate doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print(e)
			return self.send_response(code=f'500',description=e)


class AdminCandidateForJobView(BaseAPIView):
	permission_classes = (AllowAny, )
	def get(self, request, pk=None):
		try:
			job = request.query_params.get('job', '')
			if job == '':
				return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="no data found")
			candidate = CandidateDetail.objects.filter(job__id=job)
			serializer = CandidateDetailSerializer(candidate, many = True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of candidate',log_description='')
		except CandidateDetail.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="candidate doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


class JobViewSet(viewsets.ModelViewSet, BaseAPIView):
	permission_classes = (AllowAny, )
	queryset = JobPosting.objects.all()
	serializer_class = JobPostingSerializer


	def boolean(self, status):
		if status == 'true' or status == "True":
			return True
		else:
			return False

	def list(self, request, **kwargs):
		try:
			print("-----------------View Set Method---------------------")
			status_career =  request.query_params.get('status', None)
			job_title = request.query_params.get('title', None)
			location = request.query_params.get('location', None)
			query_object = Q()
			print(query_object)
			if status_career:
				query_object &= Q(status = self.boolean(status_career))
			if job_title:
				query_object &= Q(job_title = job_title)
			if location:
				query_object &= Q(location = location)

			query_object &= Q(deleted = False)

			jobs = query_jobs_by_args(query_object, **request.query_params)
			if  not jobs:
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload={},code= '',description='query_jobs_by_args Functions returning None',log_description='')
			
			serializer = JobPostingSerializer(jobs['items'], many=True)
			
			result = dict()
			result['data'] = serializer.data
			result['draw'] = jobs['draw']
			result['recordsTotal'] = jobs['total']
			result['recordsFiltered'] = jobs['count']
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=result,code= '',description='Details of Jobs',log_description='')
		except JobPosting.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Job doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print(e)
			return self.send_response(code=f'500',description=e)



class CandidateViewSet(viewsets.ModelViewSet, BaseAPIView):
	permission_classes = (AllowAny, )
	queryset = CandidateDetail.objects.all()
	serializer_class = CandidateDetailSerializer


	def boolean(self, status):
		if status == 'true' or status == "True":
			return True
		else:
			return False

	def list(self, request, **kwargs):
		try:

			job = request.query_params.get('job_title', '')
			location =request.query_params.get('location', '')
			print("-------------------", job)
			query_object = Q()
			print(query_object)
			if job != '':
				query_object &= Q(job__job_title = job)

			if location != '':
				query_object &= Q(job__location = location)

			query_object &= Q(deleted = False)
			print(query_object)

			candidate = query_candidate_by_args(query_object, **request.query_params)
			print("candidate details", candidate)
			# if  not candidate:
			# 	return self.send_response(success=True,status_code=status.HTTP_200_OK, payload={},code= '',description='query_jobs_by_args Functions returning None',log_description='')
			
			serializer = CandidateDetailSerializer(candidate['items'], many=True)
			print(serializer.data)
			
			result = dict()
			result['data'] = serializer.data
			result['draw'] = candidate['draw']
			result['recordsTotal'] = candidate['total']
			result['recordsFiltered'] = candidate['count']
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=result,code= '',description='Candidate ',log_description='')
		except JobPosting.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Candidate doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print("----------------------------------------\n", e)
			return self.send_response(code=f'500',description=e)





class EmailDataView(BaseAPIView):
	permission_classes = (AllowAny, )

	def send_mail(self, template_id, sender, recipient, data_dict):
		try:
			message = sendgrid.helpers.mail.Mail(
				from_email=sender,
				to_emails=recipient,
				subject=''
			)
			message.dynamic_template_data = data_dict
			message.template_id = template_id
			status = sg.send(message)
			print(status)
		except Exception as e:
			print("INSIDE")
			return e

	def post(self, request):
		try:
			data = request.data
			print(data)
			serializer = EmailDataSerializer(data= data)
			if serializer.is_valid():
				CandidateDetailSaved = serializer.save()
				data_dict = {
					'applicant_name' :serializer.data['name'],
					'message' : serializer.data['message'],
					'cv' : f's3.eu-central-1.amazonaws.com/corcym/{serializer.instance.cv.name}'
				}
				print(data_dict)

				mail_res = self.send_mail("d-d4c7188e448e42129b055c83521dd6fe", DEFAULT_FROM_EMAIL,  ["marcello.oppezzo@livanova.com"], data_dict)
				mail_res = self.send_mail("d-d4c7188e448e42129b055c83521dd6fe", DEFAULT_FROM_EMAIL,  ["gemma.vergara@livanova.com"], data_dict)
				mail_res = self.send_mail("d-d4c7188e448e42129b055c83521dd6fe", DEFAULT_FROM_EMAIL,  ["naeem@kaffeina.it"], data_dict)
				print(mail_res)
				mail_res2 = self.send_mail("d-b763d599c2e6411897d779255f518197", DEFAULT_FROM_EMAIL,  request.data['email'], data_dict= {})
				print(mail_res2)
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Email Data Post')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except EmailData.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Email Data  doesn't Post")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print(e)
			return self.send_response(code=f'500',description=e)


class JobListingView(BaseAPIView):
	permission_classes = (AllowAny, )
	def get(self, request, pk=None):
		try:
			jobs = JobPosting.objects.filter(status = True, deleted = False)
			serializer = JobListingSerializer(jobs, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except JobPosting.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Job doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print("Exception: ", e)
			return self.send_response(code=f'500',description=e)



class JobLocationView(BaseAPIView):
	permission_classes = (AllowAny, )
	def get(self, request, pk=None):
		try:
			# jobs = JobPosting.objects.filter(status = True, deleted = False)
			jobs = JobPosting.objects.values('location').annotate(dcount=Count('location')).order_by().all()
			job_title = JobPosting.objects.values('job_title').annotate(dcount=Count('job_title')).order_by().all()
			print(job_title)
			serializer = JobLocationSerializer(jobs, many=True)
			job_title_ser = JobTitleSerializer(job_title, many = True)
			data = {
			'location':serializer.data,
			'title':job_title_ser.data
			}
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=data,code= '',description='Details of serializer',log_description='')
		except JobPosting.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Job doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print("Exception: ", e)
			return self.send_response(code=f'500',description=e)


class DeletedJobView(BaseAPIView):
	permission_classes = (AllowAny, )
	def get(self, request, pk=None):
		try:
			if pk is not None:
				job = JobPosting.objects.get(id=pk)
				job.deleted = True
				job.save()
				print(job.status)
				return self.send_response(description= "Job Deleted successfuly",success=True,status_code=status.HTTP_200_OK, code='200')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description='Job not found ')
		except JobPosting.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Job doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print(e)
			return self.send_response(code=f'500',description=e)


class DeletedCandidateView(BaseAPIView):
	permission_classes = (AllowAny, )
	def get(self, request, pk=None):
		try:
			print("Hello corcym")
			if pk is not None:
				candidate = CandidateDetail.objects.get(id=pk)
				print(candidate)
				candidate.deleted = True
				candidate.save()
				print(candidate.deleted)
				return self.send_response(description= " Candidate Deleted successfuly",success=True,status_code=status.HTTP_200_OK, code='200')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description='candidate not found ')
		except CandidateDetail.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="candidate doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print(e)
			return self.send_response(code=f'500',description=e)


class CandidateGroupByView(BaseAPIView):
	permission_classes = (AllowAny, )
	def get(self, request, pk=None):
		try:
			# jobs = JobPosting.objects.filter(status = True, deleted = False)
			country = CandidateDetail.objects.values('job').annotate(dcount=Count('job')).order_by().all()
			serializer = CandidateJobSerializer(country, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except CandidateDetail.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Donation doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print("Exception: ", e)
			return self.send_response(code=f'500',description=e)


class JobCityListingView(BaseAPIView):
	permission_classes = (AllowAny, )
	def get(self, request, pk=None):
		try:
			jobs = JobPosting.objects.filter(status = True, deleted = False).values('location', 'job_title').distinct()
			serializer = JobCityListingSerializer(jobs, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except JobPosting.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Job doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print("Exception: ", e)
			return self.send_response(code=f'500',description=e)