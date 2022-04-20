import pdfkit


def genrate_donation_pdf(data, path):
    table_html = """<!DOCTYPE html>
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

	<h1 style="font-family: Verdana, sans-serif;color:#a50d2f; font-size:40px;"> Donation and grants request </h1>

	</div>





	<div class="myDiv" style=" font-family: Verdana, sans-serif;background:#dcdddd;margin: 0 10%;padding: 20px 20px 20px; border-left:10px solid #033c7b">
	 

	<form >

	<div>  
	  <label for="fname" style=" font-family: Verdana, sans-serif;color:black ;width:20%; display:inline-block; font-size:18px;">Organization Name:</label>
	  <input type="text" id="fname" name="fname" style=" font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px;padding: 8px; color: black;", value = '$(name)'><br><br>
	  </div>
	  
	  <div>
	  <label for="fname"style="font-family: Verdana, sans-serif;color:black;width:20%; display:inline-block; font-size:18px;">Type of Request:</label>
	  <input type="text" id="fname" name="fname" style="font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px; padding: 8px; color: black", value = '$(type_of_request)'><br><br>
	  </div>
	 
	 <div> 
	  <label for="fname" style="font-family: Verdana, sans-serif;color:black;width:20%; display:inline-block; font-size:18px;"> Email:</label>
	  <input type="text" id="fname" name="fname" style="font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px;padding: 8px; color:black", value = '$(email)'><br><br>
	</div>



	<div> 
	 <label for="fname" style="font-family: Verdana, sans-serif;color:black;width:20%; display:inline-block; font-size:18px;">Country:</label>
	  <input type="text" id="fname" name="fname" style="font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px ;padding: 8px; color:black", value = '$(country)' ><br><br>
	</div> 

	<div> 
	 <label for="fname" style="font-family: Verdana, sans-serif;color:black;width:20%; display:inline-block; font-size:18px;">Website:</label>
	  <input type="text" id="fname" name="fname" style="font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px ;padding: 8px; color:black", value = '$(website)' ><br><br>
	</div> 


	<div style = "margin-top, 10%"> 
	 <label for="fname" style="font-family: Verdana, sans-serif;color:black;width:20%; display:inline-block; font-size:18px;">Organiszation Tax Id:</label>
	  <input type="text" id="fname" name="fname" style="font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px ;padding: 8px; color:black", value = '$(organization_tax_id)' ><br><br>
	</div> 


	<div style = "margin-top, 10%"> 
	 <label for="fname" style="font-family: Verdana, sans-serif;color:black;width:20%; display:inline-block; font-size:18px;">Organization Type:</label>
	  <input type="text" id="fname" name="fname" style="font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px ;padding: 8px; color:black", value = '$(organization_type)' ><br><br>
	</div> 


	<div style = "margin-top, 10%"> 
	 <label for="fname" style="color:black;width:20%; display:inline-block; font-size:18px;">Applicant Organization address :</label>
	  <input type="text" id="fname" name="fname" style="width:71% ; color:black ; margin-top:10px ;padding: 8px; color:black", value = '$(applicant_organization_address)' ><br><br>
	</div> 
	<div style = "margin-top, 10%"> 
	 <label for="fname" style="color:black;width:20%; display:inline-block; font-size:18px;">Applicant organization name:</label>
	  <input type="text" id="fname" name="fname" style=" font-family: Verdana, sans-serif; width:71% ; color:black ; margin-top:10px ;padding: 8px; color:black", value = '$(applicant_organization)' ><br><br>
	</div>

	<div > 
	 <label for="fname" style="color:black;width:100%; display:inline-block; font-size:18px;">Description of request:</label>
	  <p style=" font-family: Verdana, sans-serif ;padding : 10px;width:92%; margin-top:20px ; color:black ;background-color: white; "> $(notes)</p><br><br>
	</div> 

	</form>



	</div>
	 

	</body>
	</html>
		"""
    new_notes = data["notes"].replace("\\n", "<br>")

    table_html = table_html.replace("$(name)", data["name"])
    table_html = table_html.replace("$(type_of_request)", data["type_of_request"])
    table_html = table_html.replace("$(email)", data["email"])
    table_html = table_html.replace("$(website)", data["website"])
    table_html = table_html.replace("$(country)", data["country"])
    table_html = table_html.replace(
        "$(organization_tax_id)", str(data["organization_tax_id"])
    )
    table_html = table_html.replace("$(organization_type)", data["organization_type"])
    table_html = table_html.replace(
        "$(applicant_organization_address)", data["applicant_organization_address"]
    )
    table_html = table_html.replace(
        "$(applicant_organization)", data["applicant_organization"]
    )
    table_html = table_html.replace("$(notes)", new_notes)

    options = {
        "page-size": "A4",
        "encoding": "utf-8",
        "margin-top": "0cm",
        "margin-bottom": "0cm",
        "margin-left": "0cm",
        "margin-right": "0cm",
    }
    pdfkit.from_string(table_html, output_path=path, options=options)
