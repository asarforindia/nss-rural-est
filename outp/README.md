# Data Dictionary

## Rural Population Ratios

The rural population ratios can be found in `rural-ratios.csv`. The file presents the ratios of rural population and
corresponding standard errors for various rounds of national sample survey

| Variable         | Description                                             |
|------------------|---------------------------------------------------------|
| *(first column)* | Name of the survey                                      |
| `ratio`          | Estimated ratio of rural population to total population |
| `err`            | Standard error of the estimated ratio                   |
 
## Response Ratios

The response ratios can be found in `response-ratios.csv` file.

| Variable        | Description                                                                                                                                         |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| `survey`        | Name of the survey                                                                                                                                  |
| `quartiles`     | Wealth quartiles q4 > q3 > q2 > q1                                                                                                                  |
| `response_code` | Reported NSS response codes:<br/> 1: co-operative and capable,<br/> 2: co-operative but not capable,<br/> 3: busy,<br/> 4: reluctant,<br/>9: others |
| `ratio`         | Estimated ratio of household that responded with `response_code` over total number of households in the wealth quartile                             |
| `err`           | Standard error of the estimated ratio                                                                                                               |

