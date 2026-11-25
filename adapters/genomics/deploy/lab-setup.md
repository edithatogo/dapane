# Set up a genomics costing template

The [lab setup video](lab-setup.mp4) follows a synthetic Panel example.

## Choose a model and format

Run `genomics-web --data-dir ./prepared` with your prepared tables and
open `http://127.0.0.1:5000/models`. Select Panel and CSV. Choose Next.

## Add a lab profile

Select **Build a profile** and enter the following synthetic values.
The screen also accepts a chosen or dropped JSON file.

| Field | Example |
| --- | --- |
| Lab name | Synthetic lab |
| Labour multiplier | 1.125 |
| Equipment life in years | 6 |
| Local categories and subcategories | `Shipping: Courier, Packaging` |

Select **Use this profile** and choose Next.

## Review and download

Confirm that the review shows **PANEL template, CSV. Lab profile
selected.** Choose **Download template** and open `panel.csv`.
This example produces 22 input rows, including Courier and Packaging
under Shipping. Unit cost cells are blank for the lab to fill using its
authorised sources.

The equivalent terminal command is `genomics-model template panel
panel.csv --profile lab-profile.json`. A profile uses the exact
multiplier as quoted text.

~~~json
{
  "lab_name": "Synthetic lab",
  "custom_categories": {"Shipping": ["Courier", "Packaging"]},
  "cost_adjustments": {
    "labor_multiplier": "1.125",
    "equipment_depreciation_years": 6
  }
}
~~~
