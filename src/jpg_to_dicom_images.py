import os
import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian, SecondaryCaptureImageStorage
import datetime
from PIL import Image
import numpy as np
import requests

jpg_file = r"C:\PythonApps\orthanc\imagenes_jpg\RS2.jpg"
dicom_file = r"C:\PythonApps\orthanc\dicoms_generados\RS2.dcm"


def convert_jpg_to_dicom(jpg_path, dicom_path, patient_name="Sr.Ramon Santiago", patient_id="4883071"):
    # Leer imagen JPG en escala de grises
    image = Image.open(jpg_path).convert("L")
    pixel_array = np.array(image)

    # Crear metadatos obligatorios
    file_meta = FileMetaDataset()
    file_meta.FileMetaInformationGroupLength = 0
    file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.ImplementationClassUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    # Crear dataset principal
    ds = FileDataset(dicom_path, {}, file_meta=file_meta, preamble=b"\0" * 128)

    # Asignar datos del paciente
    ds.PatientName = patient_name
    ds.PatientID = patient_id

    # Tiempos obligatorios
    dt = datetime.datetime.now()
    ds.StudyDate = dt.strftime('%Y%m%d')
    ds.StudyTime = dt.strftime('%H%M%S')

    # Identificadores únicos
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID

    # Otros campos necesarios
    ds.Modality = "OT"
    ds.SeriesNumber = 1
    ds.InstanceNumber = 1

    # Imagen
    ds.Rows, ds.Columns = pixel_array.shape
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.PixelData = pixel_array.tobytes()

    # Guardar archivo DICOM
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    ds.save_as(dicom_path)
    print(f"✅ DICOM guardado: {dicom_path}")

def send_to_orthanc(dicom_path, orthanc_url="http://localhost:8042", username="orthanc", password="orthanc"):
    with open(dicom_path, "rb") as f:
        response = requests.post(
            f"{orthanc_url}/instances",
            auth=(username, password),
            headers={"Content-Type": "application/dicom"},
            data=f.read()
        )
        if response.status_code == 200:
            print("✅ Archivo enviado a Orthanc con éxito.")
        else:
            print(f"❌ Error al enviar a Orthanc: {response.status_code} - {response.text}")

# ▶️ USO
#jpg = "C\PythonApps\orthanc\imagenes_jpg\RS1.jpg"
# = "C:/PythonApps/orthanc/dicoms_generados/imagen1.dcm"
convert_jpg_to_dicom(jpg_file, dicom_file, patient_name="Sr. Ramon Santiago", patient_id="4883071")
send_to_orthanc(dicom_file)