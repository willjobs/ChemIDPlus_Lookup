# ChemIDPlus Lookup
A Python script to scrape the NIH's ChemIDPlus database for the name and CASRN, given an input CSV with a list of CASRNs, names, or a mix of the two.

The ChemIDPlus CASRN/Name Checker uses the ChemIDPlus website (http://chem.sis.nlm.nih.gov/chemidplus/chemidlite.jsp) to look up the CASRN and chemical name for any CASRNs or chemical names provided in a CSV file. The results are also stored in a CSV file. <strong>The only prerequisite for running this program is that Firefox is installed.</strong>

The first time you run the program, Windows may ask you if the program can connect to any networks. Just click OK to this prompt.

The program can be run by double-clicking the .exe file itself, or by opening a new command prompt in the directory where the program is stored and typing the name of the program. The advantage of running the program from the command prompt is you can specify an alternative name for the input and output CSV files. For example, typing:

<code>ChemIDPlus_lookup "names_to_lookfor_WJ_2016-02-22.csv" "results_for_erin_2016-02-22.csv"</code>

would use the file “names_to_lookfor_WJ_2016-02-22.csv” as the input CSV file, and would output the results to the file “results_for_erin_2016-02-22.csv”. You can specify both file names, just the input file name (in which case the output file will be called ChemID_results.csv), or neither file name (in which case it will look for the input file ChemID_search.csv and will output to ChemID_results.csv).

<strong>The input file (by default, ChemID_search.csv) must be in the same directory as the program.</strong> It is a single column with no header that may contain any combination of CASRNs and chemical names. CASRNs may be formatted with or without dashes (e.g., “50000” and “50-00-0” are both fine). If it is possible that names may include commas, then all searched terms should be quoted.

While the program is running, you can look at the command prompt to see its progress and to look at any problems it has encountered while searching.

The names returned by ChemIDPlus may be synonyms of the name searched for. For example, searching for “1-(1-Phenylcyclohexyl)pyrrolidine” returns the result “Rolicyclidine”, the common name for the chemical. This is very useful, because it means you can search for any of a number of possible names a chemical might have. 

<strong>If you are searching for names, it is strongly recommended you scan through the names to make sure nothing is obviously wrong.</strong> The name search feature in ChemIDPlus sometimes returns multiple possible results and the program will always pick the first result that appears (assuming it is the best match). The command prompt window will output a message when this happens (e.g., “For ‘Abacavir’ we clicked ‘Abacavir [INN:BAN]’”). In these cases, there is a risk that ChemIDPlus may list the wrong chemical first, in which case the program would return the wrong result. As always, CASRNs are the only way to have absolute certainty the right chemical is identified.

If there is a problem with a search, the results file will contain “NO MATCH” in either the CASRN or Chemical Name column (or both) and the “Problem(s)?” column will have a short description of the problem (e.g., “No match found for searched item” or “Page too slow to load or element never loaded”).

You may see warnings in Firefox while the program is running about automated searches only being allowed every 3 seconds. This is a bug in the website (no amount of waiting seems to fix it), but the program handles it and searches continue on their own.

Note that Excel may interpret some CASRNs as dates. To get around this, import the data “From Text” rather than double-clicking (opening) the CSV directly. To import the CSV:
<ol>
<li>Click the Data tab and click “From Text”. </li>
<li>Browse to the CSV file.</li>
<li>Choose “Delimited” and check the “My data has headers” checkbox. Then click Next.</li>
<li>Choose “Comma” (and uncheck any other delimiters). Then click Next.</li>
<li>In the “Data preview” section, click the CASRN column and change the “Column data format” to “Text”. Then click Finish. Click OK to the window that pops up, or change where you want the data to be placed and then click OK.</li>
</ol>

For any questions, to report a problem (e.g., if ChemIDPlus updates their website and the code is no longer working), or to request a feature, please make a pull request.
