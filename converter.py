import fitz  # PyMuPDF
import edge_tts
import asyncio  # Required for running async functions
import os
async def pdf_to_mp3(pdf_file, output_file, voice="en-US-GuyNeural"):
    """
    Converts a PDF file to an MP3 using edge-tts for text-to-speech.

    Args:
        pdf_file (str): Path to the input PDF file.
        output_file (str): Path to the output MP3 file.
        voice (str): Voice to be used for TTS (default: "en-US-GuyNeural").
    """
    try:
        # Open the PDF and extract text
        doc = fitz.open(pdf_file)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        if not text.strip():
            raise ValueError("The PDF does not contain any readable text.")

        # Use edge-tts to convert text to MP3
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        print(f"MP3 file saved as: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main execution
if __name__ == "__main__":
    # Example usage
    input_pdf = "C:/Users/91934/Downloads/Untitled presentation.pdf"  # Replace with your PDF file path
    output_mp3 = "output.mp3"  # Replace with your desired output MP3 file path

    if not os.path.exists(input_pdf):
        print(f"Error: The file '{input_pdf}' does not exist.")
    else:
        asyncio.run(pdf_to_mp3(input_pdf, output_mp3))
