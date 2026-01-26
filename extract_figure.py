#!/usr/bin/env python3
"""
Extract the first figure from an arXiv paper PDF.
Uses --break-system-packages flag to work around externally-managed environment.
"""

import sys
import urllib.request
import os
import subprocess

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--break-system-packages", "--quiet"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def extract_figure_pymupdf(pdf_path, output_path):
    """Extract first figure using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        
        # Try to find images in the first few pages
        for page_num in range(min(5, len(doc))):
            page = doc[page_num]
            image_list = page.get_images()
            
            if image_list:
                # Get the first image
                xref = image_list[0][0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Save the image
                with open(output_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                print(f"✓ Extracted figure from page {page_num + 1}")
                doc.close()
                return True
        
        doc.close()
        return False
    except Exception as e:
        print(f"Error with PyMuPDF: {e}")
        return False

def extract_figure_pdf2image(pdf_path, output_path):
    """Extract first page as image using pdf2image."""
    try:
        from pdf2image import convert_from_path
        from PIL import Image
        
        # Convert first page to image
        images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=200)
        if images:
            images[0].save(output_path, 'PNG')
            print("✓ Extracted first page as image")
            return True
        return False
    except Exception as e:
        print(f"Error with pdf2image: {e}")
        return False

def extract_figure_pillow_pdf(pdf_path, output_path):
    """Try using PIL/Pillow directly if PDF support is available."""
    try:
        from PIL import Image
        # This might work if Pillow was compiled with PDF support
        img = Image.open(pdf_path)
        img.save(output_path, 'PNG')
        print("✓ Extracted using Pillow")
        return True
    except Exception as e:
        return False

def main():
    pdf_url = "https://arxiv.org/pdf/2408.07765.pdf"
    pdf_path = "/tmp/arxiv_2408_07765.pdf"
    output_path = "figure1.png"
    
    print("Downloading PDF...")
    try:
        urllib.request.urlretrieve(pdf_url, pdf_path)
        print(f"✓ Downloaded PDF to {pdf_path}")
    except Exception as e:
        print(f"✗ Failed to download PDF: {e}")
        return 1
    
    if not os.path.exists(pdf_path):
        print("✗ PDF file not found after download")
        return 1
    
    print("\nAttempting to extract figure...")
    
    # Try PyMuPDF first (best for extracting actual figures)
    print("Trying PyMuPDF...")
    if not extract_figure_pymupdf(pdf_path, output_path):
        # Try installing PyMuPDF if not available
        try:
            import fitz
        except ImportError:
            print("Installing PyMuPDF...")
            if install_package("PyMuPDF"):
                if extract_figure_pymupdf(pdf_path, output_path):
                    print(f"\n✓ Success! Figure saved to {output_path}")
                    return 0
    
    # Try pdf2image as fallback
    if not os.path.exists(output_path):
        print("Trying pdf2image...")
        try:
            from pdf2image import convert_from_path
            if extract_figure_pdf2image(pdf_path, output_path):
                print(f"\n✓ Success! First page saved to {output_path}")
                return 0
        except ImportError:
            print("Installing pdf2image and poppler...")
            if install_package("pdf2image"):
                # Note: poppler needs to be installed separately via brew on macOS
                print("Note: pdf2image requires poppler. Trying to install via brew...")
                try:
                    subprocess.check_call(["brew", "install", "poppler"], 
                                        stdout=subprocess.DEVNULL, 
                                        stderr=subprocess.DEVNULL)
                except:
                    print("Could not install poppler automatically. Please install manually:")
                    print("  brew install poppler")
                
                if extract_figure_pdf2image(pdf_path, output_path):
                    print(f"\n✓ Success! First page saved to {output_path}")
                    return 0
    
    print("\n✗ Could not extract figure. Please install one of:")
    print("  pip install PyMuPDF")
    print("  pip install pdf2image && brew install poppler")
    return 1

if __name__ == "__main__":
    sys.exit(main())
