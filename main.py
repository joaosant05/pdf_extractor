import fitz  # PyMuPDF
import os

def extract_main_image_from_pdf(pdf_path, output_folder, start_page, num_pages, min_width=100, min_height=100):
    # Open the PDF file
    pdf = fitz.open(pdf_path)
    
    # Loop through the specified range of pages
    for page_num in range(start_page, start_page + num_pages):
        page = pdf.load_page(page_num)
        images = page.get_images(full=True)
        
        main_image = None
        max_area = 0  # To keep track of the largest image
        
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = pdf.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_width = base_image["width"]
            image_height = base_image["height"]
            image_area = image_width * image_height
            
            # Check if the image dimensions meet the minimum size criteria
            if image_width >= min_width and image_height >= min_height:
                # Update main_image if this image is the largest found so far
                if image_area > max_area:
                    main_image = (image_bytes, image_ext, page_num, img_index)
                    max_area = image_area
        
        if main_image:
            image_bytes, image_ext, page_num, img_index = main_image
            image_filename = f"{output_folder}/page{page_num+1}_img{img_index+1}.{image_ext}"
            
            with open(image_filename, "wb") as image_file:
                image_file.write(image_bytes)
            print(f"Main image on page {page_num+1} saved as {image_filename}")
    
    pdf.close()

# Get input from the user
pdf_path = "pdf_teste.pdf"
output_folder = "images"
start_page = int(input("Enter the start page (index starting from 0): "))
num_pages = int(input("Enter the number of pages to extract: "))

# Create the output folder if it does not exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Call the function with user inputs
extract_main_image_from_pdf(pdf_path, output_folder, start_page, num_pages)
