import json
import re
import base64
import json
import io

from PyPDF2 import PdfReader, PdfWriter

class Doc_Processor:
    def __init__(self, params):
        self.params = params
        self.process_params = params['process_params']
    
    def new_name(self, root_name, index_bool, idx, prefix, suffix, delim, ext):
        fname = root_name
        if len(prefix)>0:
            fname = str(prefix)+delim+fname

        if len(suffix)>0:
            fname = fname+delim+str(suffix)

        if index_bool:
            fname = fname+delim+str(idx)+"."+ext
        else:
            fname = fname+"."+ext

        return fname
    
    def process(self, file):
        new_docs = self.file_map(file)
        return new_docs

    def file_map(self, file):
        
        if "file_map" in self.process_params.keys():
            file_map = self.process_params['file_map']
        else:
            return None

        pdf = PdfReader(file)
        filename=self.params['filename']
        root = filename.split(".")[0]
        ext = filename.split(".")[-1]

        if "prefix" in self.process_params.keys():
            prefix = self.process_params['prefix']
        else:
            prefix = ""
        if "suffix" in self.process_params.keys():
            suffix = self.process_params['suffix']
        else:
            suffix = ""

        try:
            if type(prefix)==list:
                prefix=prefix[0]
            elif type(prefix)!=str or len(prefix)<=0:
                prefix=""
        except:
            prefix=""

        try:
            if type(suffix)==list:
                suffix=suffix[0]
            elif type(suffix)!=str or len(suffix)<=0:
                suffix=""
        except:
            suffix=""

        pdf_docs = []
        for k, f in enumerate(file_map):
            new_pdf=PdfWriter()
            for p in f['pages']:
                new_pdf.add_page(pdf.pages[p])
            fname = self.new_name(root, True, k, prefix, suffix, "_", ext)
            
            outStream = io.BytesIO()
            new_pdf.write(outStream)
            outStream.seek(0)
            f['pdf'] = outStream
            f['name'] = fname
            pdf_docs.append(f)

        return pdf_docs


    