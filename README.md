# UT-LTM-Merge-Tool
A toolset to facilitate merging multiple libTAS movie files of Undertale together into one continuous TAS.

There are two parts to this tool: the Python script and the game mod. Both work together to facilitate the process of stitching two ltm files together into one.

The Python script is designed to be run in an interactive Python environment. Once this script is run, you have access to an assortment of different helpful functions. Each function is documented individually in the code. If you're looking for a more guided process, try mergingProcess().

**Important note: many of these scripts involve modifying the ltm files that you specify. It's highly suggested to make a backup of any file you intend to use with this script, as the script itself does not make any backups.**

The game mod is used to find and record RNG seeds and RNG state indexes. Please make sure to delete all of the files generated by this mod in the save folder before each run. When run, the mod outputs a file with lines of the format `state,microseconds,seed`. Please note that the microseconds are only approximate.

The general process for merging two LTM files is as follows: first, determine what the RNG seeds are at each point where they're generated. Second, work out the RNG state index from these seeds. Third, search nearby microseconds to where these calls would land in the new TAS to try and find a matching state index. Fourth, arrange variable framerates such that this time is reached down to the microsecond. Finally, append the lines into one input file and pack back into an ltm file.

There are certainly ways that this code can be improved and the process isn't the most user-friendly, but it works and is able to stitch together several long, RNG-heavy TASes together, one after the other. I will most likely add more information here at some point, including a more detailed tutorial/showcase of merging two ltm files together.

The current limitations are that the ltm files must all be manually converted to version 1.4.4 and the game mod can only be applied to version 1.001 Linux and 1.00 Windows. The RNG functions used only apply when the game is run on Linux. There are also several libTAS limitations that make this task more difficult.
