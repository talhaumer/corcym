import pdfkit

from corcym.settings import WKHTMLTOPDF


def convertTuple(tup):
    # initialize an empty string
    str = ""
    for item in tup:
        str = str + item
    return str


def genrate_contact_pdf(data, path):
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

	<h1 style="font-family: Verdana, sans-serif;color:#a50d2f; font-size:40px;"> Contact:</h1>

	</div>





	<div class="myDiv" style=" font-family: Verdana, sans-serif;background:#dcdddd;margin: 0 10%;padding: 20px 20px 20px; border-left:10px solid #033c7b">
	 

	<form >
	<div>  
	  <label for="fname" style=" font-family: Verdana, sans-serif ;color:black ;width:20%; display:inline-block; font-size:18px;">Intrest In:</label>
	  <input type="text" id="fname" name="fname" style=" font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px;padding: 8px; color: black;", value = '$(interest_in)'><br><br>
	  </div>


	<div>  
	  <label for="fname" style=" font-family: Verdana, sans-serif ;color:black ;width:20%; display:inline-block; font-size:18px;">I Would Like To:</label>
	  <input type="text" id="fname" name="fname" style=" font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px;padding: 8px; color: black;", value = '$(i_would_like_to)'><br><br>
	  </div>


	<div>  
	  <label for="fname" style=" font-family: Verdana, sans-serif ;color:black ;width:20%; display:inline-block; font-size:18px;">Name:</label>
	  <input type="text" id="fname" name="fname" style=" font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px;padding: 8px; color: black;", value = '$(name)'><br><br>
	  </div>
	  
	  <div>
	  <label for="fname"style="font-family: Verdana, sans-serif, sans-serif;color:black;width:20%; display:inline-block; font-size:18px;"> Surname:</label>
	  <input type="text" id="fname" name="fname" style="font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px; padding: 8px; color: black", value = '$(surname)'><br><br>
	  </div>
	 
	 <div> 
	  <label for="fname" style="font-family: Verdana, sans-serif;color:black;width:20%; display:inline-block; font-size:18px;"> Email:</label>
	  <input type="text" id="fname" name="fname" style="font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px;padding: 8px; color:black", value = '$(email)'><br><br>
	</div>

	<div> 
	  <label for="fname" style="font-family: Verdana, sans-serif;color:black;width:20%; display:inline-block; font-size:18px;"> Speciality:</label>
	  <input type="text" id="fname" name="fname" style="font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px;padding: 8px; color:black", value = '$(specialty)'><br><br>
	</div>

	<div> 
	 <label for="fname" style="font-family: Verdana, sans-serif;color:black;width:20%; display:inline-block; font-size:18px;">Country:</label>
	  <input type="text" id="fname" name="fname" style="font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px ;padding: 8px; color:black", value = '$(country)' ><br><br>
	</div> 

	<div> 
	 <label for="fname" style="font-family: Verdana, sans-serif;color:black;width:20%; display:inline-block; font-size:18px;">City:</label>
	  <input type="text" id="fname" name="fname" style="font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px ;padding: 8px; color:black", value = '$(city)' ><br><br>
	</div> 


	<div> 
	 <label for="fname" style="font-family: Verdana, sans-serif;color:black;width:20%; display:inline-block; font-size:18px;">Name Of Hospital:</label>
	  <input type="text" id="fname" name="fname" style="font-family: Verdana, sans-serif;width:71% ; color:black ; margin-top:10px ;padding: 8px; color:black", value = '$(name_of_hospital)' ><br><br>
	</div> 


	<div > 
	 <label for="fname" style="color:black;width:20%; display:inline-block; font-size:18px;">Comment:</label>
	  <p style=" font-family: Verdana, sans-serif ;padding : 10px;width:92%; margin-top:20px ; color:black ;background-color: white; ">  $(comment)</p><br><br>
	</div> 

	<div > 
	 <label for="fname" style="color:black;width:20%; display:inline-block; font-size:18px;">Notes:</label>
	  <p style=" font-family: Verdana, sans-serif ;padding : 10px;width:92%; margin-top:20px ; color:black ;background-color: white; ">  $(notes)</p><br><br>
	</div> 
	
	</form>



	</div>
	 

	</body>
	</html>
		"""

    new_notes = data["notes"].replace("\\n", "<br>")
    new_comments = data["comment"].replace("\\n", "<br>")

    table_html = table_html.replace("$(name)", data["name"])
    table_html = table_html.replace("$(surname)", data["surname"])
    table_html = table_html.replace("$(email)", data["email"])
    table_html = table_html.replace("$(notes)", new_notes)
    table_html = table_html.replace("$(country)", data["country"])
    table_html = table_html.replace("$(city)", data["city"])
    table_html = table_html.replace("$(comment)", new_comments)
    table_html = table_html.replace("$(name_of_hospital)", data["name_of_hospital"])
    table_html = table_html.replace("$(interest_in)", data["interest_in"])
    table_html = table_html.replace("$(i_would_like_to)", str(data["i_would_like_to"]))
    table_html = table_html.replace("$(specialty)", str(data["specialty"]))

    options = {
        "page-size": "A4",
        "encoding": "utf-8",
        "margin-top": "0cm",
        "margin-bottom": "0cm",
        "margin-left": "0cm",
        "margin-right": "0cm",
    }
    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF)
    pdfkit.from_string(
        table_html, output_path=path, configuration=config, options=options
    )
