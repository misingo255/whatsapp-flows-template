from fastapi import UploadFile

class FlowValidations:

    @classmethod
    def is_json_file(cls, file: UploadFile):
        if not file.filename.endswith(".json"):
            return False
        return True