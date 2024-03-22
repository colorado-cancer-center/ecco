<template>
  <section>
    <h2>Sources</h2>

    <AppButton
      v-tooltip="'Download all sources data in CSV format'"
      :icon="faTable"
      :to="getDownloadAll()"
      :accent="true"
    >
      Download All Data
    </AppButton>

    <p>
      Data for ECCO were gathered from several publicly available sources. Due
      to automated data collection efforts, years on sources will change over
      time. The years given here represent the most recently available data and
      reflect what is found on
      <AppLink to="https://cancerinfocus.org/"
        >Cancer InFocus: Catchment Areas</AppLink
      >. The complete years of data reflected in ECCO vary by source. Data will
      be updated as the most recent data becomes available.
    </p>
  </section>

  <section>
    <h3>Cancer Incidence and Mortality</h3>

    <h4>
      <AppLink to="https://statecancerprofiles.cancer.gov/index.html"
        >State Cancer Profiles (SCP)</AppLink
      >
    </h4>

    <p>
      SCP is an interactive map engine produced in collaboration between the
      National Cancer Institute and Centers for Disease Control and Prevention.
      It was developed with the idea to provide a geographic profile of cancer
      burden in the United States and reveal geographic disparities in cancer
      incidence, mortality, risk factors for cancer, and cancer screening,
      across different population subgroups. The target audiences are health
      planners, policy makers, and cancer information providers who need quick
      and easy access to cancer related data and maps to inform and prioritize
      investments in cancer control.
    </p>

    <p>
      Cancer incidence data from SCP used in ECCO comes from the Surveillance,
      Epidemiology, and End Results SEER*Stat Database and from the National
      Program of Cancer Registries where applicable. The most recently available
      incidence data are the 5-year average age-adjusted rates per 100,000
      people for 2016-2020.
    </p>

    <p>
      Cancer mortality data from SCP used in ECCO comes from the National Vital
      Statistics System public use data file. The most recently available
      mortality data are the 5-year age-adjusted mortality rates per 100,000
      people for 2016-2020.
    </p>
  </section>

  <section>
    <h3>
      Sociodemographics, Economics &amp; Insurnace, and Housing &amp;
      Transportation
    </h3>

    <h4>
      <AppLink to="https://data.census.gov/cedsci/"
        >American Community Survey (ACS), 5-Year Estimates, U.S. Census
        Bureau</AppLink
      >
    </h4>

    <p>
      ACS is a nationally representative sample of households that are randomly
      selected to participate. This survey provides population estimates of
      demographic information for various geographic areas, aggregated over five
      consecutive years.
    </p>

    <p>
      ECCO contains the following indicators from the ACS. The most recently
      available ACS data are the 2017-2021 5-year estimates:
    </p>

    <table>
      <thead>
        <tr>
          <th>Indicator</th>
          <th>ACS Table</th>
          <th>Population Used</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Total Population</td>
          <td>B01001</td>
          <td>Total population</td>
        </tr>
        <tr>
          <td>Under 18 Years Old</td>
          <td>B01001</td>
          <td>Total population</td>
        </tr>
        <tr>
          <td>18 to 64 Years Old</td>
          <td>B01001</td>
          <td>Total population</td>
        </tr>
        <tr>
          <td>Over 64 Years Old</td>
          <td>B01001</td>
          <td>Total population</td>
        </tr>
        <tr>
          <td>White (non-Hispanic)</td>
          <td>B01001H</td>
          <td>White alone, not Hispanic or Latino population</td>
        </tr>
        <tr>
          <td>Black (non-Hispanic)</td>
          <td>B01001B</td>
          <td>People who are Black or African American alone</td>
        </tr>
        <tr>
          <td>Hispanic</td>
          <td>B01001I</td>
          <td>People who are Hispanic or Latino</td>
        </tr>
        <tr>
          <td>Asian (non-Hispanic)</td>
          <td>B01001D</td>
          <td>People who are Asian alone</td>
        </tr>
        <tr>
          <td>Other Non-Hispanic Races</td>
          <td>B03002</td>
          <td>Total population (calculated by subtracting other indicators)</td>
        </tr>
        <tr>
          <td>Graduated High School</td>
          <td>B15003</td>
          <td>Population 25 years and over</td>
        </tr>
        <tr>
          <td>Graduated College</td>
          <td>B15003</td>
          <td>Population 25 years and over</td>
        </tr>
        <tr>
          <td>Completed a Graduate Degree</td>
          <td>B15003</td>
          <td>Population 25 years and over</td>
        </tr>
        <tr>
          <td>Annual Labor Force Participation Rate</td>
          <td>B23025</td>
          <td>Population 16 years and over</td>
        </tr>
        <tr>
          <td>Annual Unemployment Rate</td>
          <td>B23025</td>
          <td>Population 16 years and over</td>
        </tr>
        <tr>
          <td>Enrolled in Medicaid</td>
          <td>C27007</td>
          <td>Civilian noninstitutionalized population</td>
        </tr>
        <tr>
          <td>Household Income ($)</td>
          <td>B19013</td>
          <td>Households</td>
        </tr>
        <tr>
          <td>Insured</td>
          <td>B27001</td>
          <td>Civilian noninstitutionalized population</td>
        </tr>
        <tr>
          <td>Living Below Poverty</td>
          <td>B17026</td>
          <td>Families</td>
        </tr>
        <tr>
          <td>Received TANF or SNAP Public Assistance</td>
          <td>B19058</td>
          <td>Households</td>
        </tr>
        <tr>
          <td>Uninsured</td>
          <td>B27001</td>
          <td>Civilian noninstitutionalized population</td>
        </tr>
        <tr>
          <td>Crowded Homes</td>
          <td>DP04</td>
          <td>Housing units</td>
        </tr>
        <tr>
          <td>High Rent Burden</td>
          <td>B25070</td>
          <td>Renter-occupied housing units</td>
        </tr>
        <tr>
          <td>Homes without Broadband Internet</td>
          <td>DP02</td>
          <td>Households</td>
        </tr>
        <tr>
          <td>Homes without Complete Plumbing</td>
          <td>DP04</td>
          <td>Housing units</td>
        </tr>
        <tr>
          <td>Housing in Mobile Homes</td>
          <td>DP04</td>
          <td>Housing units</td>
        </tr>
        <tr>
          <td>Housing in Multi-Unit Structures</td>
          <td>DP04</td>
          <td>Housing units</td>
        </tr>
        <tr>
          <td>Median Gross Rent ($)</td>
          <td>DP04</td>
          <td>Housing units</td>
        </tr>
        <tr>
          <td>Median Home Value ($)</td>
          <td>DP04</td>
          <td>Housing units</td>
        </tr>
        <tr>
          <td>Median Monthly Mortgage ($)</td>
          <td>DP04</td>
          <td>Housing units</td>
        </tr>
        <tr>
          <td>No Household Vehicle Access</td>
          <td>B08141</td>
          <td>Workers 16 years and over in households</td>
        </tr>
        <tr>
          <td>Owner-occupied Housing Units</td>
          <td>DP04</td>
          <td>Housing units</td>
        </tr>
        <tr>
          <td>Single Parent Homes</td>
          <td>B11012</td>
          <td>Households</td>
        </tr>
        <tr>
          <td>Vacant Housing</td>
          <td>B25002</td>
          <td>Housing units</td>
        </tr>
      </tbody>
    </table>

    <h4>
      <AppLink to="https://www.bls.gov/data/"
        >U.S. Bureau of Labor Statistics (BLS)</AppLink
      >
    </h4>

    <p>
      The BLS measures labor market activity, working conditions, price changes,
      and productivity in the U.S. economy to support public and private
      decision making. ECCO uses BLS to obtain the monthly unemployment rate
      (not seasonally adjusted). This data is updated monthly and typically runs
      on a two month delay. BLS data is not included in the ECCO mapping
      applications.
    </p>
  </section>

  <section>
    <h3>Screening &amp; Risk Factors and Other Health Factors</h3>

    <h4>
      <AppLink to="https://www.cdc.gov/places/">PLACES</AppLink>
    </h4>

    <p>
      PLACES is a collaboration between CDC, the Robert Wood Johnson Foundation,
      and the CDC Foundation. PLACES provides health data for small areas across
      the country. This allows local health departments and jurisdictions,
      regardless of population size and rurality, to better understand the
      burden and geographic distribution of health measures in their areas and
      assist them in planning public health interventions.
    </p>

    <p>
      PLACES provides model-based, population-level analysis and community
      estimates of health measures to all counties, places (incorporated and
      census designated places), census tracts, and ZIP Code Tabulation Areas
      (ZCTAs) across the United States.
    </p>

    <p>
      ECCO contains the following indicators from the PLACES, which are based
      off of data from the Behavioral Risk Factor Surveillance System:
    </p>

    <table>
      <thead>
        <tr>
          <th>Indicator</th>
          <th>Most Recent Survey Variable Name</th>
          <th>Most Recent Year Used</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>
            Met Breast Screening Recommendations (Had Mammogram in Last 2 Years,
            Age 50-74)
          </td>
          <td>_MAM5023</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>
            Met Cervical Screening Recommendations (Had Pap Test in Last 3
            Years, Age 21-65)
          </td>
          <td>_RFPAP35</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>
            Met Colorectal Screening Recommendations (Met the USPSTF
            recommendations, Age 50-75)
          </td>
          <td>_CRCREC1</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Currently Smoke (adults)</td>
          <td>_RFSMOK3</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Obese (BMI over 30)</td>
          <td>_BMI5CAT</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Physically Inactive</td>
          <td>_TOTINDA</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Binge Drink</td>
          <td>_RFBING5</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Sleep &lt; 7 Hours a Night</td>
          <td>SLEPTIM1</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>History of Cancer Diagnosis</td>
          <td>CHCOCNCR</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Report Fair or Poor Overall Health</td>
          <td>_RFHLTH</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Report Frequent Physical Health Distress</td>
          <td>_PHYS14D</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Report Frequent Mental Health Distress</td>
          <td>_MENT14D</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Have Depression</td>
          <td>ADDEPEV3</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Diagnosed with Diabetes</td>
          <td>DIABETE4</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Have High Blood Pressure</td>
          <td>_RFHYPE5</td>
          <td>2019</td>
        </tr>
        <tr>
          <td>On Blood Pressure Medicine</td>
          <td>BPMEDS</td>
          <td>2019</td>
        </tr>
        <tr>
          <td>Have Coronary Heart Disease</td>
          <td>CVDCRHD4</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Had a Stroke</td>
          <td>CVDSTRK3</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Have Chronic Kidney Disease</td>
          <td>CHCKDNY2</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Diagnosed with Asthma</td>
          <td>_LTASTH1</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Have COPD</td>
          <td>CHCCOPD2</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>All Adult Teeth Lost</td>
          <td>_ALTETH3</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Had a Medical Checkup in the Last Year</td>
          <td>CHECKUP1</td>
          <td>2020</td>
        </tr>
        <tr>
          <td>Had a Dental Visit in the Last Year</td>
          <td>_DENVST3</td>
          <td>2020</td>
        </tr>
      </tbody>
    </table>
  </section>

  <section>
    <h3>Environment</h3>

    <h4>
      <AppLink
        to="https://www.ers.usda.gov/data-products/food-access-research-atlas/"
        >Economic Research Service, U.S. Department of Agriculture (USDA
        ERS)</AppLink
      >
    </h4>

    <p>
      The mission of USDA’s Economic Research Service is to anticipate trends
      and emerging issues in agriculture, food, the environment, and rural
      America and to conduct high-quality, objective economic research to inform
      and enhance public and private decision making. ERS research and analysis
      covers a broad range of economic and policy topics, including
      food/nutrition and poverty.
    </p>

    <p>
      ECCO uses the indicator Food Deserts (LILA Vehicle) from the USDA ERS. The
      most recently available data is from 2015.
    </p>

    <h4>
      <AppLink
        to="https://www.fcc.gov/general/broadband-deployment-data-fcc-form-477"
        >Federal Communications Commission (FCC)</AppLink
      >
    </h4>

    <p>
      The FCC regulates interstate and international communications by radio,
      television, wire, satellite, and cable in all 50 states, the District of
      Columbia and U.S. territories. An independent U.S. government agency
      overseen by Congress, the Commission is the federal agency responsible for
      implementing and enforcing America’s communications law and regulations.
    </p>

    <p>
      ECCO uses the FCC Form 477 broadband data on average maximum advertised
      upload and download speeds at the Census block group level. This data is
      updated twice yearly in June and December and runs about one year behind.
      FCC data is not included in the ECCO mapping applications.
    </p>

    <h4>
      <AppLink to="https://www.epa.gov/ejscreen"
        >Environmental Protection Agency (EPA) Environmental Justice Screening
        (EJScreen)</AppLink
      >
    </h4>

    <p>
      EJScreen is an EPA's environmental justice mapping and screening tool that
      provides EPA with a nationally consistent dataset and approach for
      combining environmental and demographic socioeconomic indicators.
    </p>

    <p>
      ECCO uses the 12 raw environmental justice indicator variables given at
      the Census tract level from the 2022 EJScreen dataset.
    </p>

    <h4>
      <AppLink
        to="https://www.epa.gov/ground-water-and-drinking-water/safe-drinking-water-information-system-sdwis-federal-reporting"
        >EPA Safe Drinking Water Information System (SDWIS)</AppLink
      >
    </h4>

    <p>
      The EPA's SDWIS databases store information about drinking water. The
      federal version (SDWIS/FED) stores the information the U.S. Environmental
      Protection Agency (EPA) needs to monitor approximately 156,000 public
      water systems.
    </p>

    <p>
      ECCO uses the indicator Public Water Systems Violations (Health Based)
      from the SDWIS. This data is aggregated from the most recently completed
      year back to 2016.
    </p>
  </section>

  <section>
    <h3>Facilities &amp; Providers</h3>

    <h4>
      <AppLink to="https://enviro.epa.gov/">EPA Envirofacts</AppLink>
    </h4>

    <p>
      The Envirofacts Multisystem Search integrates information from a variety
      of databases and includes latitude and longitude information. Each of
      these databases contains information about facilities that are required to
      report activity to a state or federal system.
    </p>

    <p>
      ECCO draws information on Superfund sites from the
      <AppLink to="https://www.epa.gov/enviro/sems-overview"
        >Superfund Enterprise Management System (SEMS)</AppLink
      >
      and information on facilities releasing known carcinogens from the
      <AppLink to="https://www.epa.gov/enviro/tri-model"
        >Toxic Release Inventory</AppLink
      >. Superfund site data is available in real-time; the most recently
      available Toxic Release Inventory data is from 2021.
    </p>

    <h4>
      <AppLink to="https://data.hrsa.gov/data/about"
        >Health Resources &amp; Services Administration (HRSA), Department of
        Health &amp; Human Services</AppLink
      >
    </h4>

    <p>
      HRSA programs provide health care to people who are geographically
      isolated, economically or medically vulnerable. This includes people
      living with HIV/AIDS, pregnant women, mothers and their families, and
      those otherwise unable to access high quality health care. HRSA also
      supports access to health care in rural areas, the training of health
      professionals, the distribution of providers to areas where they are
      needed most, and improvements in health care delivery.
    </p>

    <p>
      ECCO uses facility data for Federally-Qualified Health Centers (FQHC),
      FQHC Look-a-Likes (FQHC LAL), Rural Health Clinics (RHC), and Correctional
      Facility clinics. All of these facilities fall under the general
      classification of Health Professional Shortage Area (HPSA) facilities.
      This data is available in real-time, reflecting all such facilities
      currently recognized by HRSA.
    </p>

    <h4>
      <AppLink
        to="https://www.acr.org/Clinical-Resources/Lung-Cancer-Screening-Resources/LCS-Locator-Tool"
        >Lung Cancer Screening Registry (LCSR), American College of
        Radiology</AppLink
      >
    </h4>

    <p>
      The ACR Lung Cancer Screening Registry (LCSR) is designed to
      systematically audit the quality of interpretation of screening lung CT
      exams. The registry is based on the ACR Lung Imaging Reporting and Data
      System (Lung-RADS), which is the product of the ACR Lung Cancer Screening
      Committee subgroup on Lung-RADS. This Lung-RADS system is a quality
      assurance tool designed to standardize lung cancer screening CT reporting
      and management recommendations, reduce confusion in lung cancer screening
      CT interpretations and facilitate outcome monitoring. The ACR LCSR will
      capture Lung-RADS recommendations and monitor and compare appropriate use
      of Lung-RADS
    </p>

    <p>
      ECCO uses the location data for Lung Cancer Screening Sites from the LCSR.
      This data is available in real-time, reflecting active lung cancer
      screening locations in the LCSR.
    </p>

    <p>
      <i>
        Note: Not all lung cancer screening sites are required to be a part of
        the LCSR. The ACR estimates that the LCSR reflects between 80%-90% of
        all active sites in the nation.</i
      >
    </p>

    <h4>
      <AppLink to="https://nppes.cms.hhs.gov/#/"
        >National Plan &amp; Provider Enumeration System (NPPES)</AppLink
      >
    </h4>

    <p>
      Centers for Medicare &amp; Medicaid Services CMS has developed the NPPES
      to assign unique identifiers to health care providers. The National
      Provider Indentifier (NPI) has been the standard identifier for all
      HIPAA-covered entities (health care providers) since May 23, 2007. Small
      health plans were required to obtain and use an NPI by May 23, 2008.
    </p>

    <p>
      ECCO uses the location data for gastroenterologists and colon &amp; rectal
      surgeons from the NPPES. This data is available in real-time, reflecting
      all practicing providers.
    </p>

    <h4>
      <AppLink
        to="https://www.fda.gov/radiation-emitting-products/consumer-information-mqsa/search-certified-facility"
        >United States Food and Drug Administration (FDA)</AppLink
      >
    </h4>

    <p>
      The Mammography Quality Standards Act requires mammography facilities
      across the nation to meet uniform quality standards. Congress passed this
      law in 1992 to assure high-quality mammography for early breast cancer
      detection, which can lead to early treatment, a range of treatment
      options, and increased chances of survival. Under the law, all mammography
      facilities must: 1) be accredited by an FDA-approved accreditation body,
      2) be certified by FDA, or its State, as meeting the standards, 3) undergo
      an annual MQSA inspection, and 4) prominently display the certificate
      issued by the agency.
    </p>

    <p>
      ECCO uses the location data for Mammography Sites from the FDA Certified
      Mammography Facilities list. This data is updated on a weekly basis to
      reflect real-time presence of mammography facilities.
    </p>
  </section>
</template>

<script setup lang="ts">
import { faTable } from "@fortawesome/free-solid-svg-icons";
import { getDownloadAll } from "@/api";
import AppButton from "@/components/AppButton.vue";
import AppLink from "@/components/AppLink.vue";
</script>
