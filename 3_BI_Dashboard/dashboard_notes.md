# A Few Notes on Building the Dashboard

Hey there! Thanks for taking a closer look at the project. This file is just a quick, casual walkthrough of my thought process while building the Power BI part of the pipeline. I ran into a few interesting challenges and learned a ton, so I wanted to share some of the highlights.

## 1. Figuring Out the Data Model (Star vs. Snowflake)

Initally, my `DimProgram` table had the university's full text name right in it, and the relationship was built on that. It worked, it was a ***Star* Schema**, but it felt a bit clunky. I knew using numbers is faster than strings (thanks MySQL), so I decided to refactor the model to use the numeric `UniversityID` instead. *More Power Query experience!*

1.  I used the **Merge Queries** feature to temporarily bring the `UniversityID` from `DimUniversity` into my `DimProgram` table by matching them on the university name.
2.  Once I had the numeric ID, I just removed the now-redundant text `UniversityName` column from `DimProgram`.
3.  Then I went back to the Model view and created the new, clean relationship based on the ID.

Now my **Star** was a **Snowflake** and since I am in Finland, so that fits like a glove!

## 2. Playing Around with some DAX Measures

I am more used to Python libraries for visualisation (Plotly & Dash), so no drag-and-drop. And I wanted to bring some programatic features to make the report smarter:

### The Dynamic Title
The "Deep Dive" page felt a bit static. I thought it would be cool if the title could change based on what you picked in the slicer.

**The Code:**
```dax
Dynamic Page Title = 
IF(
    HASONEVALUE(DimUniversity[UniversityName]),
    "Deep Dive: " & SELECTEDVALUE(DimUniversity[UniversityName]),
    "Please Select a University to Begin"
)
```
`HASONEVALUE` just checks if one university is selected. If it is, the formula builds the nice "Deep Dive: [University Name]" title. If not, it shows the "Please Select a University to Begin".

### The Heatmap Percentage
It is summer and hot and soon really hot, so we need a heat-map. As I limited my data collection (for my own sanity) I found showing the total number of applicants one of few options. However that was misleading since big universities would have big numbers everywhere! But one could show the calculated the percentage of a university's *own* applicant pool.

```dax
% of University's Applicants by Age Group = 
VAR TotalApplicantsForUniversity =
    CALCULATE(
        [Total Applicants],
        ALL(DimApplicantAgeGroup) -- Compared to all AgeGroups
    )
RETURN
    DIVIDE(
        [Total Applicants],
        TotalApplicantsForUniversity
    )
```
The `VAR` part calculates the total number of applicants for the university in the tables row, basically ignoring the age group filter for a moment. Then, it just divides the number for the specific age group cell by that university's total. This gives a fair, normalized percentage that powers the heatmap, so you can see real patterns instead of just big numbers.

## 3. Thoughts on the Dashboard Design

My main goal was to make something easy and hopefully useful (and if nothing else, a little flashy for my portfolio)!

1.  **The Overview:** Landing page and overall trend with some highlighted KPIs.
2.  **The Deep Dive:** The second page is for a more detailed overview on one university. The "Top 10 Programs" table was so you don't have to scroll through a giant list to find the important stuff.
3.  **The Demographics:** Last but not least, if so many people apply, who are they? This last page gives an overview on age groups and genders and you can get more specific with the filters.

With more resources I think grabbing more data, specifically georaphical data from Vipunen would be a interesting. Seeing from were and at what age people are applying to each program would be interesting for me, and *probably* valuable for marketing too!