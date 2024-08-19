from pathlib import Path
from typing import Optional

import requests
from pydantic import BaseModel

import config


class AttachmentMethods:
    def attachment_content(self, content_id: str, **kwargs) -> tuple[Optional[str], Optional[bytes]]:
        response = requests.get(config.URL_FILESTORE + content_id, verify=False, **kwargs)
        source_filename = requests.utils.unquote(
            list(
                filter(
                    lambda x: x.startswith('filename'),
                    response.headers.get('Content-Disposition', '').split('; '),
                )
            )[0].split("''")[1]
        )
        fc = Path(source_filename)
        if response.content:
            return fc.stem[: config.ATTACHMENT_FILENAME_MAX_LENGTH] + fc.suffix, response.content
        else:
            return None, None

    def attachment_save(
        self, content_id: str, new_filename: str = None, path: Path = None, **kwargs
    ) -> tuple[bool, Optional[str]]:
        source_filename, content = self.attachment_content(content_id, **kwargs)
        filename = new_filename or source_filename
        if path:
            filename = Path(path, filename)
        if content:
            with open(filename, 'wb') as f:
                f.write(content)
                return True, filename.name
        else:
            return False, None

    def download(self, filename: str = None, path: Path = None) -> tuple[bool, Optional[str]]:
        if not any(hasattr(self, 'id'), hasattr(self, 'contentId')):
            raise AttributeError('No contentId or id attribute')
        content_id = getattr(self, 'id', getattr(self, 'contentId'))
        return self.attachment_save(content_id=content_id, new_filename=filename, path=path)


class AttachmentModel(BaseModel, AttachmentMethods):
    contentId: str
    URL: str
    detachedSignature: str

    def attachment_content(self, content_id: str = None, url: str = None, **kwargs):
        FILENAME_MAX_LENGTH = 100
        if content_id:
            url = config.URL_FILESTORE + content_id

        response = requests.get(url, **kwargs)
        filename_content = requests.utils.unquote(
            list(
                filter(
                    lambda x: x.startswith('filename'),
                    response.headers.get('Content-Disposition', '').split('; '),
                )
            )[0].split("''")[1]
        )

        fc = Path(filename_content)
        if response.content:
            return ''.join([fc.stem[:FILENAME_MAX_LENGTH], fc.suffix]), response.content
        else:
            return None, None

    def attachment_content_save(
        self, content_id: str = None, url: str = None, filename=None, path=None, **kwargs
    ):
        filename_content, content = self.attachment_content(content_id, url, **kwargs)

        filename = filename or filename_content
        if path:
            filename = path + filename

        if content:
            with open(filename, 'wb') as f:
                f.write(content)
            return True, filename
        else:
            return False, None
