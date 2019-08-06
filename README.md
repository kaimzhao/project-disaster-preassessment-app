# README for DamSmartAss #

## Overview ##

Natural disasters, like wildfires, floods, and earthquakes, are tragic events that can harm people, damage property, and strain society in complex ways. Emergency relief organizations exist to mitigate these problems. For our project, we attempt to reduce the strain on society of natural disasters by facilitating the assessment of damage to property, specifically real estate. Our app gives assessors, who are associated either with a relief organization or an insurance company, the means to automatically generate damage assessment reports for residential properties.

The assessor arrives at a residential parcel, takes a picture, and after confirming the relevant address, our app returns a damage assessment report complete with:
- *before* and *after* images,
- category of the damage source (e.g., fire, flood, earthquake),
- and summary details of the property (e.g., property square footage).

By using our application to generate damage assessment reports, provide value to three stakeholders:
* Insurance claim assessors benefit from a streamlined workflow
* Policyholders benefit from faster payment adjudication
* Emergency relief organizations (nonprofits or governmental agencies) benefit from greater insight into damage intensity and efficacy of preventative measures

Our prototype involves the following APIs:
- [Google Vision AI](https://cloud.google.com/vision/)
- [Google Reverse Geocoding](https://developers.google.com/maps/documentation/geocoding/intro#ReverseGeocoding)
- [Google Street View Static](https://developers.google.com/maps/documentation/streetview/intro)
- [Zillow Get Deep Search Results](https://www.zillow.com/howto/api/GetDeepSearchResults.htm)

USAGE NOTE: You will need to provide your own API keys, and modify credentials file path for API calls to your keys. Also note two limitations:
* Our prototype does not yet support Apple's HEIC format (default on iPhone), users must first select JPEG as output format (Settings -> Camera -> Format -> "Most Compatible").
* Our prototype requires that searched properties are included in Zillow database (e.g., commercial property will throw an error)
* Our prototype requires that geolocation (latitude/longitude) is included in image file's metadata.

Anchor links here:
- [How it works](#How-it-works)
- [Future Development](#Future-Development)
- [Terms of Use](#Terms-of-Use-for-APIs)
- [Contributions](#Contributions)

## Schematic
<img src="https://github.com/miecky/project-client_project/blob/master/Image/process_flow.png?raw=true">

## How it works

### On first click:
* **Input**: User takes in-app photo of damage site
* **Action**: Image is passed to Google Vision AI API; latitude/longitude information is extracted from image file and passed to Google Reverse Geocoding API
* **Outputs**:
  * New report is generated, photo is attached to report as the *after* photo
  * Google Vision AI returns type of damage incurred, attached to report as "Damage Source" (e.g., fire or flood)
  * Google Reverse Geocoding API returns a list of street addresses for nearest properties

### On second click:
* **Input**: User selects relevant address from the list output in Step 1 (NOTE: user can manually input address if not included in list)
* **Action**: Address is passed to two APIs: Google Street View Static and Zillow Get Deep Search Results.
* **Outputs**:
  * Google Street View Static API returns an image of the property prior to the disaster, attached to report as *before* photo
  * Zillow Get Deep Search Results API returns property information, attached to report as "Property Details"

### Outcome
#### Input Page
<img src="https://github.com/miecky/project-client_project/blob/master/Image/sample_home_page.png?raw=true">

#### Address Validation Page
<img src="https://github.com/miecky/project-client_project/blob/master/Image/address_validation.png?raw=true">

#### Output Page
<img src="https://github.com/miecky/project-client_project/blob/master/Image/sample_report.png?raw=true">

## Future development

### Supporting damages estimate using regression

**Current state:** The final output of our application is an automatically generated, pre-filled report with information relevant for claims assessment. Whether a claim gets approved and the amount of reimbursement still needs to be manually determined by the assessor.

**Future state:** If we create a database of reports after they are completed by the assessor,* we will have *before*/*after* photos associated with damage source that are labeled with reimbursement amounts. This database can support regression analysis to provide estimated reimbursement amount for future reports. These reimbursement estimates can be used:
* by assessors as a benchmark for future reimbursement determinations
* by relief organizations (e.g., FEMA) to assess damage intensity by area and efficacy of local preparation measures, which enables more efficient and timely allocation of resources for prevention and relief.

\* The reports in this database must exclude Zillow information, per its Terms of Service prohibiting the storage of their data.

### Supporting multi-photo assessment reports

**Current state:** Our application automatically generates a damage-assessment report upon capturing a photo. This means that each picture taken prompts a completely new report, which precludes multiple photographs being attached to a singular report.

**Future state:** Suppose there is exterior damage and interior damage, or damage to the garage as well as the house, a complete damage assessment report would require multiple photographs. To do this, ___


### Expand beyond exterior damage

**Current state:** Our application is currently limited to exterior damage. If we could access *before* photographs of the property interior, we could extend our functionality to interior damage.

**Future state:** Zillow has access to interior images of properties, but does not provide them via API per its terms of service. Were we to partner with Zillow and satisfy their legal and business concerns associated with interior images, we could use them to extend our functionality to interior damage assessment.

### Expand beyond residential property

**Current state:** For context, our application provides property details to assessors using data from Zillow, which is limited to residential real estate.

**Future state:** To extend application functionality to commercial, industrial, agricultural real estate, we would need to obtain property details from another source.

### Automatically ingesting insurance policy associated with property

**Current state:** We do not have access to insurance policies for properties. Many insurance policies, for example, exclude flood damage from coverage.

**Future state:** If we partnered with insurance companies, we could include this information in reports.

### Reducing API fees for image classification

**Current state:** Our application uses Google Vision AI to classify the source of damage, which incurs fees with use.

**Future state:** If we substituted a proprietary image-classification algorithm here, we can avoid these fees.



## Terms of Use for APIs

Terms of Use for Google APIs ([Maps APIs](https://cloud.google.com/maps-platform/terms/), [Vision AI](https://developers.google.com/terms/):
- Terms of Use and Privacy Policy for our application must be publicly available.
- It must be explicitly stated in our application's Terms of Use that by using our application, users are bound by Google’s [Terms of Service](https://developers.google.com/terms/).
- It must be noted in Privacy Policy that we are using the Google API(s), and incorporate by reference the Google [Privacy Policy](https://policies.google.com/privacy).

Terms of use for [Zillow API](https://www.zillow.com/howto/api/APITerms.htm):
- Zillow data must not constitute the primary functionality nor the majority of content on mobile apps
- We may not retain copies of Zillow data
- We may not use Zillow data exclusively on the backend
- We must adhere to branding guidelines wherever Zillow data is present

Include disclaimers (e.g., sections 7,8 on Zillow Terms of Use)

### API associated fees

#### Google Vision AI
| 0–1,000                                | 1,000–5,000,000                      | 5,000,000+                         |
|----------------------------------------|----------------------------------------|----------------------------------|
| Free | 0.0015 USD per each (1.50 USD per 1000) | 0.001 USD per each (1.00 USD per 1000) |


#### Google Geocoding API

| 0–100,000                              | 100,001–500,000                        | 500,000+                         |
|----------------------------------------|----------------------------------------|----------------------------------|
| 0.005 USD per each (5.00 USD per 1000) | 0.004 USD per each (4.00 USD per 1000) | [Contact Sales](https://enterprise.google.com/maps/contact-form/index.html) for volume pricing |

#### Google Street View Static API

| 0–100,000                              | 100,001–500,000                        | 500,000+                         |
|:--------------------------------------:|:--------------------------------------:|:--------------------------------:|
| 0.014 USD per each (14.00 USD per 1000) | 0.0112 USD per each (11.20 USD per 1000) | [Contact Sales](https://enterprise.google.com/maps/contact-form/index.html) for volume pricing |




## Contributions

**Mikhail Lenko:** established process to retrieve desired information from Google Vision AI and Zillow Get Deep Search APIs using Python, wrote ReadMe.
**Ryan Leyba:** prototyped function for extracting geolocation data from smart phone image files using Python, created presentation deck.
**Kai Zhao:** established process to retrieve desired information from Google Maps APIs, integrated backend code using Python Flask, built front-end user interface with HTML/CSS.

And special thanks to **Alison Norris** for front-end consultation and **James Huang** for front- and backend consultation.
