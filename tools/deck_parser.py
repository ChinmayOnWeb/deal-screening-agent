"""
Extracts text from pitch deck PDFs.
Uses PyMuPDF for text + Llama 4 Vision on Groq for image-based slides.
"""

import io
import re
import os
import time
import base64
from dotenv import load_dotenv

load_dotenv()


def extract_text_with_pymupdf(uploaded_file) -> str:
    """Method 1: PyMuPDF text extraction."""
    try:
        import fitz

        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""

        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            if page_text.strip():
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page_text

        doc.close()
        return text.strip()

    except Exception as e:
        print(f"PyMuPDF failed: {str(e)}")
        return ""


def extract_blocks_with_pymupdf(uploaded_file) -> str:
    """Method 2: PyMuPDF block extraction."""
    try:
        import fitz

        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""

        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("blocks")
            page_text = ""
            for block in blocks:
                if block[6] == 0:
                    page_text += block[4] + "\n"
            if page_text.strip():
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page_text

        doc.close()
        return text.strip()

    except Exception as e:
        print(f"Block extraction failed: {str(e)}")
        return ""


def extract_dict_with_pymupdf(uploaded_file) -> str:
    """Method 3: PyMuPDF dict/span extraction."""
    try:
        import fitz

        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""

        for page_num in range(len(doc)):
            page = doc[page_num]
            page_dict = page.get_text("dict")
            page_text = ""
            for block in page_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        for span in line["spans"]:
                            span_text = span.get("text", "").strip()
                            if span_text:
                                line_text += span_text + " "
                        if line_text.strip():
                            page_text += line_text.strip() + "\n"
            if page_text.strip():
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page_text

        doc.close()
        return text.strip()

    except Exception as e:
        print(f"Dict extraction failed: {str(e)}")
        return ""


def render_page_as_small_image(page, max_size_bytes=2_500_000) -> str:
    """
    Render a single PDF page as a compressed base64 image.
    Keeps reducing quality until under size limit.
    """
    import fitz

    # Try different zoom levels (lower = smaller file)
    for zoom in [1.5, 1.0, 0.75, 0.5]:
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        size_bytes = len(img_base64)

        if size_bytes < max_size_bytes:
            print(f"    📐 Zoom {zoom}x → {round(size_bytes/1024)}KB")
            return img_base64

    # Last resort: tiny JPEG
    try:
        from PIL import Image

        mat = fitz.Matrix(0.5, 0.5)
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))

        # Convert to JPEG with low quality
        jpeg_buffer = io.BytesIO()
        img.save(jpeg_buffer, format="JPEG", quality=50)
        jpeg_bytes = jpeg_buffer.getvalue()
        img_base64 = base64.b64encode(jpeg_bytes).decode("utf-8")

        print(f"    📐 JPEG fallback → {round(len(img_base64)/1024)}KB")
        return img_base64

    except Exception:
        return None


def extract_with_llama_vision(uploaded_file) -> str:
    """
    Use Llama 4 Vision on Groq to read image-based slides.
    Sends ONE image per request to stay under size limits.
    """
    try:
        import fitz
        from groq import Groq

        GROQ_KEY = os.getenv("GROQ_API_KEY")
        if not GROQ_KEY:
            return "ERROR: No GROQ_API_KEY found."

        client = Groq(api_key=GROQ_KEY)

        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        total_pages = len(doc)
        text = ""

        VISION_MODELS = [
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
        ]

        print(f"📸 Processing {total_pages} pages with Llama 4 Vision...")
        print(f"📤 Sending 1 image per request (to stay under size limit)")

        for page_num in range(total_pages):
            page = doc[page_num]

            # Render page as small image
            img_base64 = render_page_as_small_image(page)

            if not img_base64:
                text += f"\n--- Page {page_num + 1} ---\n"
                text += "[Could not render this page]\n"
                continue

            print(f"\n  📤 Page {page_num + 1}/{total_pages} ({round(len(img_base64)/1024)}KB)")

            # Try each vision model
            success = False
            for model in VISION_MODELS:
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = client.chat.completions.create(
                            model=model,
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": (
                                                f"This is slide {page_num + 1} of a startup pitch deck. "
                                                "Extract ALL text, numbers, and data. Include:\n"
                                                "- Headings and titles\n"
                                                "- Body text and bullet points\n"
                                                "- Numbers, metrics, percentages\n"
                                                "- Chart/graph labels and values\n"
                                                "- Names and titles of people\n"
                                                "- Company names and logos\n\n"
                                                "Just extract the content. Do NOT describe design or layout."
                                            )
                                        },
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/png;base64,{img_base64}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            temperature=0.2,
                            max_tokens=1024
                        )

                        slide_text = response.choices[0].message.content
                        text += f"\n--- Page {page_num + 1} ---\n"
                        text += slide_text
                        print(f"  ✅ Page {page_num + 1} extracted via {model.split('/')[-1]}")
                        success = True

                        # Rate limit pause
                        time.sleep(3)
                        break

                    except Exception as e:
                        error_msg = str(e)
                        if "429" in error_msg or "rate_limit" in error_msg.lower():
                            wait_time = 15 * (attempt + 1)
                            print(f"  ⏳ Rate limited. Waiting {wait_time}s...")
                            time.sleep(wait_time)
                        elif "413" in error_msg or "too_large" in error_msg.lower():
                            print(f"  ⚠️ Still too large for {model.split('/')[-1]}, trying next model...")
                            break
                        else:
                            print(f"  ❌ {model.split('/')[-1]}: {error_msg}")
                            break

                if success:
                    break

            if not success:
                text += f"\n--- Page {page_num + 1} ---\n"
                text += "[Could not extract this slide]\n"

        doc.close()
        return text.strip()

    except ImportError as e:
        return f"ERROR: Missing package - {str(e)}"
    except Exception as e:
        return f"ERROR: Vision extraction failed - {str(e)}"


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Main extraction function.
    Tries text methods first, falls back to Llama 4 Vision.
    """

    # Method 1: PyMuPDF text
    text = extract_text_with_pymupdf(uploaded_file)
    if text and len(text) > 200:
        print(f"✅ Method 1 (text): {len(text)} chars")
        return text

    # Method 2: PyMuPDF blocks
    text2 = extract_blocks_with_pymupdf(uploaded_file)
    if text2 and len(text2) > 200:
        print(f"✅ Method 2 (blocks): {len(text2)} chars")
        return text2

    # Method 3: PyMuPDF dict
    text3 = extract_dict_with_pymupdf(uploaded_file)
    if text3 and len(text3) > 200:
        print(f"✅ Method 3 (dict): {len(text3)} chars")
        return text3

    # Method 4: Llama 4 Vision
    print("📸 Text methods failed. Using Llama 4 Vision...")
    vision_text = extract_with_llama_vision(uploaded_file)

    if vision_text and not vision_text.startswith("ERROR") and len(vision_text) > 100:
        print(f"✅ Method 4 (Llama Vision): {len(vision_text)} chars")
        return vision_text

    # Return best of whatever we got
    all_results = [text or "", text2 or "", text3 or "", vision_text or ""]
    best = max(all_results, key=len)

    if best and len(best) > 0:
        return best + "\n\n[WARNING: Limited text extracted. Consider pasting manually.]"

    return ("ERROR: Could not extract text from this PDF. "
            "Please paste the content manually using the text box above.")


def extract_key_fields(deck_text: str) -> dict:
    """Quick regex extraction for common pitch deck fields."""
    fields = {
        "has_revenue_mention": bool(
            re.search(r'\$[\d,.]+[KkMmBb]?\s*(ARR|MRR|revenue)', deck_text, re.IGNORECASE)
        ),
        "has_funding_ask": bool(
            re.search(r'(raising|seeking|round)\s*\$?[\d,.]+[KkMmBb]?', deck_text, re.IGNORECASE)
        ),
        "has_team_slide": bool(
            re.search(r'(team|founders|leadership|about us)', deck_text, re.IGNORECASE)
        ),
        "has_traction": bool(
            re.search(r'(traction|growth|users|customers|revenue)', deck_text, re.IGNORECASE)
        ),
        "has_market_size": bool(
            re.search(r'(TAM|SAM|SOM|market size|billion|trillion)', deck_text, re.IGNORECASE)
        ),
        "page_count": deck_text.count("--- Page"),
        "word_count": len(deck_text.split()),
        "has_image_only_pages": "[Could not extract" in deck_text
    }

    return fields