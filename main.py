import fitz
import os
import hashlib
from PIL import Image, ImageOps
import io
import numpy as np
import pdfplumber
import pandas as pd

def is_black_background(img):
    img_gray = img.convert('L')
    img_array = np.array(img_gray)
    
    black_pixels = np.sum(img_array < 50)
    total_pixels = img_array.size
    black_ratio = black_pixels / total_pixels
    
    return black_ratio > 0.8

def invert_colors(img):
    img_inverted = ImageOps.invert(img.convert('RGB'))
    return img_inverted

def save_image_as_png(image_bytes, output_path):
    with Image.open(io.BytesIO(image_bytes)) as img:
        if img.mode not in ['RGB', 'RGBA']:
            img = img.convert('RGB')
        
        if is_black_background(img):
            img = invert_colors(img)
        
        img.save(output_path, format="PNG")

def extract_tables_with_pdfplumber(pdf_path, output_folder, start_page, num_pages):
    tables_output_folder = os.path.join(output_folder, "tables")

    if not os.path.exists(tables_output_folder):
        os.makedirs(tables_output_folder)

    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(start_page, start_page + num_pages):
            page = pdf.pages[page_num]
            tables = page.extract_tables()

            if tables:
                for i, table in enumerate(tables):
                    df = pd.DataFrame(table)
                    excel_filename = f"{tables_output_folder}/page{page_num+1}_table{i+1}.xlsx"
                    df.to_excel(excel_filename, index=False)
                    print(f"Table on page {page_num+1} saved as {excel_filename}")
            else:
                print(f"No tables found on page {page_num+1}.")

def extract_main_image_from_pdf(pdf_path, output_folder, start_page, num_pages):
    pdf = fitz.open(pdf_path)
    saved_hashes = set()
    
    for page_num in range(start_page, start_page + num_pages):
        page = pdf.load_page(page_num)
        images = page.get_images(full=True)
        
        main_image = None
        max_area = 0
        
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = pdf.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_width = base_image["width"]
            image_height = base_image["height"]
            image_area = image_width * image_height
            
            if image_area > max_area:
                main_image = (image_bytes, image_ext, page_num, img_index)
                max_area = image_area
        
        if main_image:
            image_bytes, image_ext, page_num, img_index = main_image
            
            image_hash = hashlib.sha256(image_bytes).hexdigest()
            
            if image_hash not in saved_hashes:
                image_filename = f"{output_folder}/page{page_num+1}_img{img_index+1}.png"
                save_image_as_png(image_bytes, image_filename)
                
                print(f"Main image on page {page_num+1} saved as {image_filename}")
                saved_hashes.add(image_hash)
            else:
                print(f"Duplicate image on page {page_num+1} skipped.")
    
    pdf.close()

# Exemplo de uso
pdf_path = "teste_2.pdf"
output_folder = "output"
start_page = int(input("Enter the start page (index starting from 0): "))
num_pages = int(input("Enter the number of pages to extract: "))

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

extract_main_image_from_pdf(pdf_path, output_folder, start_page, num_pages)
extract_tables_with_pdfplumber(pdf_path, output_folder, start_page, num_pages)
