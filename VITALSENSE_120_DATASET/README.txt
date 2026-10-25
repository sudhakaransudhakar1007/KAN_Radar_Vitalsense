

This documentation file was generated on date in 2026-01-29



GENERAL INFORMATION
-------------------

1. Title of Dataset: A New Dataset for Millimeter-Wave Radar Vital Sensing With Reference Signals".


2. Authorship: 


	Name: Ruochen Wu
	Institution: Universitat Politècnica de Catalunya
	Email:ruochen.wu@UPC.edu
	ORCID:0000-0003-0852-424X

	Name:Laura Miró
	Institution: Universitat Politècnica de Catalunya
	Email:
	ORCID:0009-0000-1524-2940

	Name: Albert Aguasca
	Institution:Universitat Politècnica de Catalunya
	Email: aguasca@tsc.upc.edu
	ORCID:0000-0003-2079-4322

	Name: Antoni Broquetas
	Institution:Universitat Politècnica de Catalunya
	Email:
	ORCID:0000-0001-9801-9145

	Name: Cosme Garcia Garcia
	Institution: Hospital Universitari Germans Trias i Pujol
	Email:
	ORCID:0000-0001-6330-1677

	Name: Montse Najar
	Institution: Universitat Politècnica de Catalunya
	Email:
	ORCID:0000-0003-3507-5689


DESCRIPTION
-----------

1. Dataset language: English


2. Abstract:
Millimeter-wave (mmWave) radar is widely recognized as a critical tool for contactless, continuous human sensing across multiple scenarios. Yet, there is a lack of high-quality datasets with synchronized reference measurements, especially at higher frequencies, which are essential for advancing signal processing methods and improving the retrieval of vital parameters. To address this gap, we introduce a new radar vital signal dataset collected with simultaneous reference recordings. The dataset is derived from measurements acquired using a custom-built, noncommercial radar system developed by our laboratory (CommSensLab-UPC) specifically for biomedical applications. The implemented Frequency-Modulated Continuous Wave (FMCW) radar system operates at 120 GHz within the industrial, scientific, and medical (ISM) band. This high center frequency provides superior spatial resolution and sensitivity to millimeter-level chest movements, enabling more precise monitoring of cardiopulmonary dynamics compared to lower-frequency systems. In parallel, a monitoring system records reference physiological signals, including electrocardiograms, respiratory traces, pulse waveforms, and blood pressure values. Under a predefined protocol, a professional clinician collected data from 24 healthy subjects, ensuring methodological rigor. The release of this dataset aims to facilitate the development and validation of advanced radar signal processing algorithms, thereby enhancing the contribution of radar technologies to hemodynamic monitoring and autonomic nervous system assessment.



3. Keywords:
Cardiopulmonary activity; Radar-based healthcare; FMCW radar; Vital signs monitoring; Dataset  


4. Date of data collection (single date or date range):
[Format YYYY-MM-DD or YYYY-MM-DD - YYYY-MM-DD]

5. Date of dataset publication:
2026-01-29


6. Funding sources: 
[Repeat the information for each funder if applicable]

	Funding agency: Agencia Estatal de Investigación
	Project number: PID2020-117303GB-C21

	Funding agency: Agencia Estatal de Investigación
	Project number: PID2022-138648OB-I00

	Funding agency: Agencia Estatal de Investigación
	Project number: PID2024-161188OB-C21



7. Geographic location/s of data collection:
[Latitude, longitude, city, region, country, etc.]



ACCESS INFORMATION
------------------

1. Creative Commons License of the dataset:
[Recommended license CC0]


2. Dataset DOI: 10.34810/data2962


Previous Dataset: 
10.21227/wq68-sv85 
Published at IEEE Dataport 
https://ieee-dataport.org/open-access/new-dataset-millimeter-wave-radar-vital-sensing-reference-signals


3. Related publication:
[Bibliographic citation of the publication related with the dataset in your discipline's standard style, including DOI.]

4. Link to related datasets: 
[(E.g. Datasets from the same project) according to this structure.]





VERSIONING AND PROVENANCE
-------------------------

1. Last modification date:

2. Was data derived from another source?:


3. Additional related data collected that was not included in the current data package:


METHODOLOGICAL INFORMATION
--------------------------
[Describe the methodology used to generate the dataset.]
[Do not copy paste the methods section from a pending publication unless you have made sure that you can do that: some journals may consider this as a publication, and will not accept the manuscript.]
[If you want to refer to an article that has not been accepted for publication yet, include as much information as you have at the moment.]
[Include the DOI in the citation.]


1. Description of methods used for collection-generation of data: 
[Include references, in your discipline's standard style, to publications or other documentation containing experimental design or protocols used in data collection.]


2. Methods for processing the data: 
[Describe how the submitted data were generated from the raw or collected data.]


3. Instrument- or software- specific information needed to interpret the data:
[Include version of software. If software is not openly available, explain where to get the software. Consider changing the format of the dataset into an open format (recommended).] 


4. Instruments, calibration and standards information:


5. Environmental or experimental conditions:
[E.g.: atmospheric influences, computational environment, etc.]


6. Quality-assurance procedures performed on the data:



FILE OVERVIEW
--------------


The dataset contains measurements from 24 subjects, with a total of 4 minutes per subject across the *Resting* and *Apnea* scenarios. The data and parameters are stored in lightweight `.mat` files that can be read directly in MATLAB, and the entire dataset is about 31 MB


1. Explain the file naming convention, if applicable:


2. File List:


The file structure is
```
VITALSENSE_120_DATASET
├── VS01
│  ├── VS01_Resting.mat
│  ├── VS01_Resting_Mindray.mat
│  ├── VS01_Apnea.mat
│  └── VS01_Apnea_Mindray.mat
...
├── VS24
│  ├── VS24_Resting.mat
│  ├── VS24_Resting_Mindray.mat
│  ├── VS24_Apnea.mat
│  └── VS24_Apnea_Mindray.mat
└── Subject Information.xlsx
   ├── Subject Info
   ├── Radar Parameters 
   └── Reference Parameters
        


3. Relationship between files:


4. File format:

TABULAR DATA-SPECIFIC INFORMATION
---------------------------------
This section should be created for each file or dataset that requires explanation of variables (typically, tabular data). All variables should be described. Include the measurement units.]


1. File name:


2. Number of rows and columns: 


3. Variable list:
[Repeat the structure for each variable.]

	Variable name:
        Description: 
	Measurement units or value labels:


4. Missing data codes:
[Repeat the structure for each code or symbol.]        
	
	Code or symbol:        
	Definition:

        
5. Specialized formats or abbreviations used:



MORE INFORMATION 

----------------
### Code

In this repository you can find the reference code used for the technical validation of breathing and cardiac signals sparation ([`VS_separation`](https://github.com/Rc-W024/VS_DATASET/blob/main/VS_separation.m)) and synchronization study ([`TechValidation`](https://github.com/Rc-W024/VS_DATASET/blob/main/TechValidation.m)). In addition, the script [`PlotVS`](https://github.com/Rc-W024/VS_DATASET/blob/main/PlotVS.m) for data visualization is also included in the repository which can be used by configuring the subject and/or scenarios which shall be viewed.

In particular, this repository also contains the code for the validation of the radar micro-motion sensing part in the paper ([`Test_speaker`](https://github.com/Rc-W024/VS_DATASET/blob/main/Test_speaker.m)), which contains the entire process from the raw beat tone signal to the target displacement signal extraction. The [raw data](https://github.com/Rc-W024/VS_DATASET/blob/main/Loudspeaker.bin) acquired during the test measurement is also included.

The mmWave radar measured data were recorded by means of a high speed digitizer, which is managed by a **C++** based executable. The validation code was written and tested using **MATLAB** *R2024b* for Microsoft Windows.


