# Estimating Rural Population Ratio and Survey Response Rate

This repository contains the code and results for estimating the following quantities.
1. Ratio of rural population to overall population in India with standard errors
2. Ratio of survey responses by wealth quartiles in terms of cooperation and capability and related standard errors

We use various nationally representative survey to derive the above estimates for India. We use the following survey
name abbreviations to reference these surveys:

| Survey                                                                          | Abbreviated Name |
|---------------------------------------------------------------------------------|------------------|
| NSS 68: SCHEDULE 1.0: CONSUMER EXPENDITURE                                      | `NSS-68-CE`      |
| NSS 68: SCHEDULE 10: EMPLOYMENT AND UNEMPLOYMENT                                | `NSS-68-EU`      |
| NSS 72: SCHEDULE 21.1: DOMESTIC TOURISM EXPENDITURE                             | `NSS-72-DT`      |
| NSS 72: SCHEDULE 1.5: HOUSEHOLD EXPENDITURE ON SERVICES AND DURABLE GOODS       | `NSS-72-HE`      |
| NSS 75: SCHEDULE 25.2: HOUSEHOLD SOCIAL CONSUMPTION: EDUCATION                  | `NSS-75-SCE`     |
| NSS 75: SCHEDULE 25.0: HOUSEHOLD SOCIAL CONSUMPTION: HEALTH                     | `NSS-75-SCH`     |
| NSS 76: SCHEDULE 1.2: DRINKING WATER, SANITATION, HYGIENE and HOUSING CONDITION | `NSS-76-DW`      |
| NSS 76: SCHEDULE 26: SURVEY OF PERSONS WITH DISABILITIES                        | `NSS-76-PD`      |

For more information about National Sample Surveys (NSS), check the [NSSO website](https://mospi.gov.in/NSSOa)

# Repository Structure

* `reader.py`: provides functions to read data from various rounds of National Sample Surveys into a standard format
* `calc.py`: provides the `calc.estimate` function to derive estimates of the above estimands from survey microdata
* `main.py`: callable module. Use `python main.py --help` for argument details
* `cache/`: cache directory for storing intermediate files. In this repository, we use it to share cleaned files 
from different rounds of NSS surveys, such that the readers can reproduce the work without having to download microdata
* `outp/`: provides estimated values. Check respective [README.md](./outp/README.md) file for details