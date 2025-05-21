import os
import pydicom
from pydicom.dataset import Dataset, FileDataset
import datetime
import time
from PIL import Image
import numpy as np

def create_dicom_from_jpg(jpg_path, output_path, patient_name="Ramon Santiago", patient_id="4883071"):
    # Abrir imagen y convertir a escala de grises
    image = Image.open(jpg_path).convert('L')
    pixel_array = np.array(image)

    # Crear dataset DICOM
    file_meta = pydicom.Dataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.ImplementationClassUID = pydicom.uid.generate_uid()

    # Crear objeto DICOM
    ds = FileDataset(output_path, {}, file_meta=file_meta, preamble=b"\0" * 128)

    # Fecha y hora
    dt = datetime.datetime.now()
    ds.ContentDate = dt.strftime('%Y%m%d')
    ds.ContentTime = dt.strftime('%H%M%S')

    # Identificación del paciente
    ds.PatientName = patient_name
    ds.PatientID = patient_id

    # Otros atributos obligatorios para visores DICOM
    ds.StudyInstanceUID = pydicom.uid.generate_uid()
    ds.SeriesInstanceUID = pydicom.uid.generate_uid()
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
    ds.Modality = "OT"  # OT = Other
    ds.SeriesNumber = "1"
    ds.InstanceNumber = "1"

    # Información del contenido de la imagen
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.Rows, ds.Columns = pixel_array.shape
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.PixelData = pixel_array.tobytes()

    # Guardar archivo DICOM
    ds.save_as(output_path)
    print(f"✅ DICOM guardado: {output_path}")

# USO EJEMPLO:
create_dicom_from_jpg("C:\PythonApps\orthanc\jpg_images\RS1.jpg", "C:\PythonApps\orthanc\dico_converted\RX1.dcm", patient_name="Ramon Santiago", patient_id="4883071")
