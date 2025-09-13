from celery import shared_task
from django.shortcuts import redirect
from .models import Profile, PDFFile,MP3File
import fitz  # PyMuPDF
import edge_tts
import os
import asyncio

from celery import Celery

app = Celery('pdftomp3')
app.config_from_object('celery_config')

#@shared_task
@app.task 
def convert_pdf_to_mp3_task(voice,pdf_path, title, profile):
    async def pdf_to_mp3(pdf_file, output_file, voice="en-US-GuyNeural"):
        try:
            doc = fitz.open(pdf_file)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()

            # Use edge-tts to convert text to MP3
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_file)
            print(f"MP3 file saved as: {output_file}")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Set the output MP3 file path
    output_dir = "media/mp3s"  # Ensure this directory exists
    title = title.replace(" ", "_")
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist
    output_file = os.path.join(output_dir, f"{title}_{voice}.mp3")

    # Run the conversion task asynchronously
    loop = asyncio.get_event_loop()
    loop.run_until_complete(pdf_to_mp3(pdf_path, output_file,voice))

    user = Profile.objects.get(id=profile)
    mp3_file = MP3File(mp3_file=f"mp3s/{title}_{voice}.mp3", title=title, user=user)
    mp3_file.save()

    return {"status": "success","id":mp3_file.id,"user":profile} # Return the instance for further use