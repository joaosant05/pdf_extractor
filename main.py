import fitz
import os
import hashlib

def extract_main_image_from_pdf(pdf_path, output_folder, start_page, num_pages, min_width=0, min_height=0):
    pdf = fitz.open(pdf_path)
    saved_hashes = set()
    
    # Loop para ler páginas
    for page_num in range(start_page, start_page + num_pages):
        page = pdf.load_page(page_num)
        images = page.get_images(full=True)
        
        main_image = None
        max_area = 0  # Prioriza a maior imagem
        
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = pdf.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_width = base_image["width"]
            image_height = base_image["height"]
            image_area = image_width * image_height
            
            if image_width >= min_width and image_height >= min_height:
                if image_area > max_area:
                    main_image = (image_bytes, image_ext, page_num, img_index)
                    max_area = image_area
        
        if main_image:
            image_bytes, image_ext, page_num, img_index = main_image

            image_hash = hashlib.sha256(image_bytes).hexdigest()
            
            if image_hash not in saved_hashes:
                image_filename = f"{output_folder}/page{page_num+1}_img{img_index+1}.{image_ext}"
                with open(image_filename, "wb") as image_file:
                    image_file.write(image_bytes)
                print(f"Main image on page {page_num+1} saved as {image_filename}")

                saved_hashes.add(image_hash)
            else:
                print(f"Duplicate image on page {page_num+1} skipped.")
    
    pdf.close()

pdf_path = "teste_2.pdf"
output_folder = "images"
start_page = int(input("Enter the start page (index starting from 0): "))
num_pages = int(input("Enter the number of pages to extract: "))

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

extract_main_image_from_pdf(pdf_path, output_folder, start_page, num_pages)
