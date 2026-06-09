import fitz, os, base64

doc = fitz.open('general Revision Sheet.pdf')
for pi in range(len(doc)):
    page = doc[pi]
    imgs = page.get_images(full=True)
    if imgs:
        print(f"Page {pi+1} has {len(imgs)} images")
        for i, img in enumerate(imgs):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            # Just print some info for now
            print(f"  Img {i}: {base_image['width']}x{base_image['height']} {base_image['ext']}")
    if pi > 20: break # Only check first 20 pages
