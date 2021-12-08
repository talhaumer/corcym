import pdfkit
# from corcym.settings import WKHTMLTOPDF



def convertTuple(tup):
        # initialize an empty string
    str = ''
    for item in tup:
        str = str + item
    return str


def genrate_pdf(data, path):
	try:
		table_html = '''<!DOCTYPE html>
		<html>
		<head>
		<style>
		*{margin: 0mm; padding:0mm ;}
		  
		  @page {
		        size: A4; / Change from the default size of A4 /
		        margin: 0mm; / Set margin on each page /
		      }
		    
		    
		</style>
		</head>
		<body>
		<img src="https://corcym.s3.eu-central-1.amazonaws.com/media/header.png" alt="Paris" style="width:100% ; margin-bottom: 3%">
		<div style="margin: 1% 10%;">
		<h1 style="font-family: Verdana, sans-serif;color:#a50d2f; font-size:40px;"> Application details </h1>
		</div>
		<div class="myDiv" style=" font-family: Verdana, sans-serif;background:#dcdddd;margin: 0 10%;padding: 20px 20px 20px; border-left:10px solid #033c7b">
		 
		<form >
		<div>  
		  <label for="fname" style=" font-family: Verdana, sans-serif;color:black ;width:20%; display:inline-block; font-size:18px;">Job Title:</label>
		  <input type="text" id="fname" name="fname" style=" font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px;padding: 8px; color: black;", value = '$(job_title)'><br><br>
		  </div>
		<div>  
		  <label for="fname" style=" font-family: Verdana, sans-serif;color:black ;width:20%; display:inline-block; font-size:18px;">First Name:</label>
		  <input type="text" id="fname" name="fname" style=" font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px;padding: 8px; color: black;", value = '$(name)'><br><br>
		  </div>
		  
		  <div>
		  <label for="fname"style="font-family: Verdana, sans-serif;color:black;width:20%; display:inline-block; font-size:18px;">Last Name:</label>
		  <input type="text" id="fname" name="fname" style="font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px; padding: 8px; color: black", value = '$(last_name)'><br><br>
		  </div>
		 
		 <div> 
		  <label for="fname" style="font-family: Verdana, sans-serif;color:black;width:20%; display:inline-block; font-size:18px;"> Email:</label>
		  <input type="text" id="fname" name="fname" style="font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px;padding: 8px; color:black", value = '$(email)'><br><br>
		</div>
		<div > 
		 <label for="fname" style="color:black;width:20%; display:inline-block; font-size:18px;">Message:</label>
		  <p style=" font-family: Verdana, sans-serif ;padding : 10px;width:92%; margin-top:20px ; color:black ;background-color: white; ">  $(notes)</p><br><br>
		</div> 
		
		</form>
		</div>
		 
		</body>
		</html>
			'''

		new_notes = data['notes'].replace("\\n", "<br>")
		
		table_html = table_html.replace("$(name)", convertTuple(data['first_name']))
		table_html = table_html.replace("$(last_name)", convertTuple(data['last_name']))
		table_html = table_html.replace("$(email)", convertTuple(data['email']))
		table_html = table_html.replace("$(notes)", new_notes)
		table_html = table_html.replace("$(job_title)", convertTuple(data['job_title']))
		options = {
	    'page-size':'A4',
	    'encoding':'utf-8', 
	    'margin-top':'0cm',
	    'margin-bottom':'0cm',
	    'margin-left':'0cm',
	    'margin-right':'0cm'
	    }
		# config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF)
		# pdfkit.from_string(table_html, output_path = path,configuration = config,  options=options)
		pdfkit.from_string(table_html, output_path = path,  options=options)

		return "True"
	except Exception as e:
		return str(e)
