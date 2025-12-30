import base64
import io
from typing import Optional
from pypdf import PdfReader
from docx import Document


class ResumeProcessor:
    """Process resumes from various formats (PDF, DOCX, text)"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = io.BytesIO(pdf_content)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(docx_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            docx_file = io.BytesIO(docx_content)
            doc = Document(docx_file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error extracting text from DOCX: {str(e)}")
    
    @staticmethod
    def process_resume(
        resume_text: Optional[str] = None,
        resume_file: Optional[str] = None,
        file_extension: Optional[str] = None
    ) -> str:
        """
        Process resume from text or file
        
        Args:
            resume_text: Plain text resume
            resume_file: Base64 encoded file content
            file_extension: File extension (pdf, docx, etc.)
        
        Returns:
            Extracted resume text
        """
        if resume_text:
            return resume_text.strip()
        
        if resume_file:
            try:
                # Decode base64
                file_content = base64.b64decode(resume_file)
                
                # Determine file type and extract
                if file_extension:
                    ext = file_extension.lower()
                    if ext == "pdf":
                        return ResumeProcessor.extract_text_from_pdf(file_content)
                    elif ext in ["docx", "doc"]:
                        return ResumeProcessor.extract_text_from_docx(file_content)
                    else:
                        # Try to decode as text
                        return file_content.decode('utf-8', errors='ignore')
                else:
                    # Try PDF first, then DOCX, then text
                    try:
                        return ResumeProcessor.extract_text_from_pdf(file_content)
                    except:
                        try:
                            return ResumeProcessor.extract_text_from_docx(file_content)
                        except:
                            return file_content.decode('utf-8', errors='ignore')
            except Exception as e:
                raise ValueError(f"Error processing resume file: {str(e)}")
        
        raise ValueError("Either resume_text or resume_file must be provided")

