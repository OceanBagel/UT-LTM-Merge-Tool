from tarfile import open as topen
import configparser
import os
import shutil

def randomizeMicrosState(micros):
    """
    Takes an integer number of microseconds and returns an index representing the initial RNG state.

    Args:
        micros (int): An integer number of microseconds.
        seed (int, optional): The

    Returns:
        int: The RNG state for the input microseconds.
    """
    seed = randomizeMicrosSeed(micros)

    stateIndex = seedToState(seed)

    return stateIndex

def randomizeMicrosSeed(micros):
    """
    Takes an integer number of microseconds and returns an index representing the RNG seed.

    Args:
        micros (int): An integer number of microseconds.

    Returns:
        int: The RNG seed for the input microseconds.

    """
    timeOffset = 0

    # This can be up to 64 bits
    timeVariable = micros + timeOffset

    # We also need the lower 32 bits of timeVariable
    timeVariable32 = timeVariable & 0xFFFFFFFF

    # This is the formula used by randomize() to calculate the RNG seed.
    seed = (timeVariable32 * 0x10000 | timeVariable32 >> 0x10) ^\
        ((timeVariable >> 0x20) + timeVariable32)

    # The true seed is only the lower 32 bits of the calculated value.
    seed = seed & 0xFFFFFFFF

    return seed

def seedToState(seed):
    """
    Converts from a seed to an RNG state index. This formula was datamined by colinator27.
    Note that this is version-dependent and is designed for 1.001 Linux running on Linux.
    Also note that this is not the full RNG state but each state index correlates to exactly one state.

    Args:
        seed (int): The RNG seed.

    Returns:
        int: The RNG state index.

    """
    # The state index correlates to the seed like this:
    stateIndex = (((seed * 0x343FD) + 0x269EC3) >> 0x10) & 0xFFFF

    return stateIndex

def trySeedsUpTo(microsMax):
    """
    Outputs a text file with lines of micros,seed from 0 to microsMax.

    Args:
        microsMax (int): An integer number of microseconds representing the maximum microseconds to be output.

    Returns:
        None.

    File outputs:
        seeds.csv: A text file output in the working directory, with each line formatted as micros,seed,state from 0 micros up to microsMax.
    """
    with open("seeds.csv", "w") as fid:
        fid.write("micros,seed\n")
        for i in range(microsMax):
            fid.write("{0},{1}\n".format(i, randomizeMicrosSeed(i), randomizeMicrosState(i)))

def trySeedsUpTo_SeedsOnly(microsMax):
    """
    Outputs a text file with lines of seeds from 0 to microsMax.

    Args:
        microsMax (int): An integer number of microseconds representing the maximum microseconds to be output.

    Returns:
        None.

    File outputs:
        seeds.csv: A text file output in the working directory, with each line listing one seed ordered from 0 micros up to microsMax.
    """
    with open("seeds.csv", "w") as fid:
        fid.write("seed\n")
        for i in range(microsMax):
            fid.write("{0}\n".format(randomizeMicrosSeed(i)))

def trySeedsRange(microsMin, microsMax):
    """
    Outputs a text file with lines of micros,seed from microsMin to microsMax.

    Args:
        microsMin (int): An integer number of microseconds representing the minimum microseconds to be output.
        microsMax (int): An integer number of microseconds representing the maximum microseconds to be output.

    Returns:
        None.

    File outputs:
        seeds.csv: A text file output in the working directory, with each line formatted as micros,seed,state from microsMin up to microsMax.
    """
    with open("seeds.csv", "w") as fid:
        fid.write("micros,seed\n")
        for i in range(microsMin, microsMax):
            fid.write("{0},{1}\n".format(i, randomizeMicrosSeed(i), randomizeMicrosState(i)))

def matchSeed(seedToMatch, startMicros, searchSizeLimit = 10000000):
    """
    Finds the next microsecond value with a seed that matches seedToMatch starting with the given value of startMicros.

    Args:
        seedToMatch (int): The seed that is to be matched.
        startMicros (int): The minimum value of microseconds to check.
        searchSizeLimit (int, optional): The maximum number of seeds to check. Defaults to 10000000.

    Returns:
        int: Returns the micros of the earliest matching seed. If no seed is found, returns -1.
    """
    for i in range(startMicros, startMicros + searchSizeLimit):
        if randomizeMicrosSeed(i) == seedToMatch:
            return i
    return -1

def matchState(stateToMatch, startMicros, searchSizeLimit = 10000000):
    """
    Finds the next microsecond value with a seed that matches seedToMatch starting with the given value of startMicros.

    Args:
        seedToMatch (int): The seed that is to be matched.
        startMicros (int): The minimum value of microseconds to check.
        searchSizeLimit (int, optional): The maximum number of seeds to check. Defaults to 10000000.

    Returns:
        int: Returns the micros of the earliest matching seed. If no seed is found, returns -1.
    """
    for i in range(startMicros, startMicros + searchSizeLimit):
        if randomizeMicrosState(i) == stateToMatch:
            return i
    return -1

def findRepeats(startMicros = 0, limit = 1000000):
    """
    Searches for a repeated run of RNG seeds starting from startMicros.

    Args:
        startMicros (int, optional): The minimum value of microseconds to check. Defaults to 0.
        limit (int, optional): The maximum value of micros to check. Defaults to 1000000.

    Returns:
        int, int: Returns the two millisecond values where seeds start repeating. If no repeat is found, returns 0, 0.
    """
    j = 0
    runningList = []
    firstMatch = 0
    currentlyMatching = 0
    maxPercent = 0
    k = startMicros

    while k < startMicros + limit:
        for i in range(k, k + limit):
            runningList += [randomizeMicrosState(i)]

            if currentlyMatching == 0:
                if i != k and randomizeMicrosState(i) == runningList[j]: # Found a match
                    firstMatch = i
                    currentlyMatching = 1

            elif currentlyMatching == 1:
                j += 1

                if randomizeMicrosState(i) != runningList[j]: # Lost matching
                    firstMatch = 0
                    currentlyMatching = 0
                    j = 0

                else:
                    if j / firstMatch > maxPercent:
                        maxPercent = j / (firstMatch - k)
                        print("{} {:%}".format(i, maxPercent))

                if j == firstMatch and currentlyMatching == 1: # Found a full match
                    return i, firstMatch
        k += 1
        j = 0
        runningList = []
        firstMatch = 0
        currentlyMatching = 0
        maxPercent = 0
    return 0, 0

def findDuplicates(startMicros = 0, limit = 1000000):
    """
    Searches for a duplicate run of RNG states starting from startMicros.

    Args:
        startMicros (int, optional): The minimum value of microseconds to check. Defaults to 0.
        limit (int, optional): The maximum value of micros to check. Defaults to 1000000.

    Returns:
        int, int: Returns the number of repeats and the micros where the repeat happens.
    """

    currentValue = randomizeMicrosState(startMicros)
    duplicates = 1
    duplicatesStart = startMicros
    bestDuplicates = 1
    bestDuplicatesStart = startMicros

    for i in range(startMicros + 1, startMicros + limit):
        if i % 10000000 == 0:
            print(i, currentValue)
        if randomizeMicrosState(i) == currentValue:
            duplicates += 1
            if duplicates > bestDuplicates:
                bestDuplicates = duplicates
                bestDuplicatesStart = duplicatesStart
                print(bestDuplicates, bestDuplicatesStart)
        else:
            duplicates = 1
            duplicatesStart = i
        currentValue = randomizeMicrosState(i)
    if bestDuplicates == 1:
        return "No duplicates found out of {} seeds checked".format(limit)
    else:
        return"{0} duplicates starting at {1} microseconds out of {2} seeds checked".format(bestDuplicates, bestDuplicatesStart, limit)

def matchSeed_ms(seedToMatch, startMicros, searchSizeLimit = 100000000):
    """
    Finds the next microsecond value with a seed that matches seedToMatch starting with the given value of startMicros.
    This function only returns multiples of 1000 microseconds.

    Args:
        seedToMatch (int): The seed that is to be matched.
        startMicros (int): The minimum value of microseconds to check.
        searchSizeLimit (int, optional): The maximum number of seeds to check. Defaults to 10000000.

    Returns:
        int: Returns the micros of the earliest matching seed that is a multiple of 1000. If no seed is found, returns -1.
    """
    for i in range(startMicros, startMicros + searchSizeLimit):
        if i % 1000 != 0:
            continue

        if randomizeMicrosState(i) == seedToMatch:
            return i
    return -1

def openltm(filePath):
    """
    Opens each of the files in the ltm file and returns their file IDs. Run closeltm() on the output dict to close all of the open files.

    Args:
        filePath (str): The file path of the ltm file.

    Returns:
        dict: {filePath : [ltmFID, annotationsPath, configPath, editorPath, inputsPath]} A dictionary with the file path as the key
              and a list of the ltm file id followed by the contents paths as the value
    """
    ltmFID = topen(filePath) # Open as a tarfile

    dirPath = "__temp/" + filePath.removesuffix(".ltm")

    ltmFID.extractall(dirPath + "/")

    annotationsPath = dirPath + "/" + "annotations.txt"
    configPath = dirPath + "/" + "config.ini"
    editorPath = dirPath + "/" + "editor.ini"
    inputsPath = dirPath + "/" + "inputs"

    return {filePath : [ltmFID, annotationsPath, configPath, editorPath, inputsPath]}

def closeltm(fidDict, filesToClose = None, merge = False):
    """
    Closes each of the files in the supplied dict, using the format supplied by openltm().
    Optionally takes a list of files to close, otherwise closes all files.

    Args:
        fidDict (dict): Dictionary of format {filePath : [ltmFID, annotationsFID, configFID, editorFID, inputsFID]}.
        filesToClose (list, optional): A list of file paths to be closed. Defaults to None, in which case all files in the dict are closed.
        merge (dict or bool, optional): Whether or not to update the ltm file by merging the extracted files back together. {filepath: bool} or bool

    Returns:
        dict: fidDict with the closed files removed.
    """
    if filesToClose == None:
        filesToClose = list(fidDict.keys()) # If None, select all files in the dict

    if merge == False:
        merge = dict(zip(filesToClose, [False]))
    elif merge == True:
        merge = dict(zip(filesToClose, [True]))

    for filePath in filesToClose:
        if filePath in fidDict.keys(): # Silently ignore file paths that were already removed
            [ltmFID, annotationsPath, configPath, editorPath, inputsPath] = fidDict[filePath]

            # # Close all inside files first
            # annotationsFID.close()
            # configFID.close()
            # editorFID.close()
            # inputsFID.close()

            # Then close the ltm file
            ltmFID.close()

            # Merge the files into a new ltm if requested
            if merge[filePath]:

                ltmFID = topen(filePath.removesuffix(".ltm"), "w:gz")
                try:
                    ltmFID.add(annotationsPath, arcname = "annotations.txt")
                    os.remove(annotationsPath)
                except FileNotFoundError:
                    pass
                try:
                    ltmFID.add(configPath, arcname = "config.ini")
                    os.remove(configPath)
                except FileNotFoundError:
                    pass
                try:
                    ltmFID.add(editorPath, arcname = "editor.ini")
                    os.remove(editorPath)
                except FileNotFoundError:
                    pass
                try:
                    ltmFID.add(inputsPath, arcname = "inputs")
                    os.remove(inputsPath)
                except FileNotFoundError:
                    pass
                os.rmdir(inputsPath.removesuffix("/inputs"))
                ltmFID.close()
                os.remove(filePath)
                os.rename(filePath.removesuffix(".ltm"), filePath)

            # Otherwise delete the extracted files
            else:
                try:
                    os.remove(annotationsPath)
                except FileNotFoundError:
                    pass
                try:
                    os.remove(configPath)
                except FileNotFoundError:
                    pass
                try:
                    os.remove(editorPath)
                except FileNotFoundError:
                    pass
                try:
                    os.remove(inputsPath)
                except FileNotFoundError:
                    pass
                os.rmdir(inputsPath.removesuffix("/inputs"))

            # Remove the dict element
            fidDict.pop(filePath)

    return fidDict

def safeFileDelete(filepath):
    """
    Deletes the given file if it exists, otherwise does nothing.

    Args:
        configFID (_io.TextIOWrapper): File ID of the configuration file

    Returns:
        0
    """

def getLibtasVersion(configPath):
    """
    Returns the libTAS version number from the configuration file.

    Args:
        configFID (_io.TextIOWrapper): File ID of the configuration file

    Returns:
        str: The libTAS version number (e.g. "1.3.4")
    """
    configData = configparser.ConfigParser()
    configData.optionxform = str

    with open(configPath):
        configData.read(configPath)

    # These are all stored by configparser as strings, so no need to convert types.
    major = configData["General"]["libtas_major_version"]
    minor = configData["General"]["libtas_minor_version"]
    patch = configData["General"]["libtas_patch_version"]

    return major + "." + minor + "." + patch

def getFPSConfig(configPath):
    """
    Returns the FPS numerator, denominator, and whether variable fps is enabled.

    Args:
        configFID (_io.TextIOWrapper): File ID of the configuration file

    Returns:
        int, int, bool: FPS numerator, denominator, variable FPS enabled
    """
    configData = configparser.ConfigParser()
    configData.optionxform = str
    with open(configPath):
        configData.read(configPath)

    # FPS numerator and denominator should always be there
    num = configData.getint("General","framerate_num")
    den = configData.getint("General","framerate_den")

    # Variable FPS might not be there
    variable_framerate = configData.getboolean("General", "variable_framerate", fallback=False)
    return num, den, variable_framerate

def setFPSConfig(configPath, num = None, den = None, variable_framerate = None):
    """
    Sets the FPS numerator, denominator, variable fps enabled

    Args:
        configPath (str): The path to config.ini.
        num (int, optional): The FPS numerator.
        den (int, optional): The FPS denominator.
        variable_framerate (bool, optional): Whether variable fps is enabled or not.

    Returns:
        None.
    """
    configData = configparser.ConfigParser()
    configData.optionxform = str
    #with open(configPath) as configFID:
    configData.read(configPath)
    if num != None:
        configData["General"]["framerate_num"] = str(num)
    if den != None:
        configData["General"]["framerate_den"] = str(den)
    if variable_framerate != None:
        configData["General"]["variable_framerate"] = str(variable_framerate).lower()
    with open(configPath, "w") as configFID:
        configData.write(configFID, space_around_delimiters=False)

    return

def getStartTime(configPath):
    """
    Returns the start time in units of microseconds.

    Args:
        configPath (str): Path to config file.

    Returns:
        int: Start time in microseconds

    """
    configData = configparser.ConfigParser()
    configData.optionxform = str
    configData.read(configPath)
    try:
        sec = configData.getint("General","initial_monotonic_time_sec")
        nsec = configData.getint("General","initial_monotonic_time_nsec")
    except KeyError: # This is for pre-monotonic time versions
        sec = configData.getint("General","initial_time_sec")
        nsec = configData.getint("General","initial_time_nsec")


    micros = int(sec * 1000000 + nsec / 1000)

    return micros


def getEndTime(configPath):
    """
    Returns the end time in units of microseconds. This is different from the length and represents the clock time at the end.

    Args:
        configPath (str): Path to config file.

    Returns:
        int: End time in microseconds

    """
    configData = configparser.ConfigParser()
    configData.optionxform = str
    configData.read(configPath)
    try:
        sec = configData.getint("General","initial_monotonic_time_sec")
        nsec = configData.getint("General","initial_monotonic_time_nsec")
    except KeyError: # This is for pre-monotonic time versions
        sec = configData.getint("General","initial_time_sec")
        nsec = configData.getint("General","initial_time_nsec")

    lsec = configData.getint("General","length_sec")
    lnsec = configData.getint("General","length_nsec")

    micros = int(lsec * 1000000 + lnsec / 1000) + int(sec * 1000000 + nsec / 1000)

    return micros



def addRerecordCounts(configPath1, configPath2, ouputConfigPath):
    """
    Adds the rerecord counts and the savestate frame counts together and puts them in the output file in preparation for merging

    Args:
        configPath1 (str): Path to config 1.
        configPath2 (str): Path to config 2.
        ouputConfigPath (str): Path to config output.

    Returns:
        None.

    """
    configData1 = configparser.ConfigParser()
    configData1.optionxform = str
    configData2 = configparser.ConfigParser()
    configData2.optionxform = str
    outconfigData = configparser.ConfigParser()
    outconfigData.optionxform = str

    configData1.read(configPath1)
    configData2.read(configPath2)
    outconfigData.read(ouputConfigPath)
    rr1 = configData1["General"]["rerecord_count"]
    ss1 = configData1["General"]["savestate_frame_count"]
    rr2 = configData2["General"]["rerecord_count"]
    ss2 = configData2["General"]["savestate_frame_count"]
    outconfigData["General"]["rerecord_count"] = str(int(rr1) + int(rr2))
    outconfigData["General"]["savestate_frame_count"] = str(int(ss1) + int(ss2))
    with open(ouputConfigPath, "w") as configFID:
        outconfigData.write(configFID, space_around_delimiters=False)

    return




def mergeLibtasFiles(firstFilepath, secondFilepath, outputFilepath):
    """
    Takes two filepaths to .ltm files and merges the two into an output .ltm file.
    This function takes into account the version of the ltm file and uses variable fps to get the correct output.
    This function does not take into account

    Args:
        firstFilepath (str): Path to the first .ltm file.
        secondFilepath (str): Path to the second .ltm file.
        outputFilepath (str): Path to the output .ltm file. Will be deleted if it exists.

    Returns:
        None.

    File outputs:
        outputFilepath: The merged .ltm file. Note, this will be overwritten without prompting.
    """
    # First open the two file paths to merge
    fidDict = openltm(firstFilepath)
    fidDict.update(openltm(secondFilepath))

    # Retrieve version numbers
    versions = ["0.0.0", "0.0.0", "0,0,0"] # First file, second file, output file
    fps_nums = [60, 60, 60]
    fps_dens = [1, 1, 1]
    varfpses = ["true", "true", "true"]

    versions[0] = getLibtasVersion(fidDict[firstFilepath][2])
    versions[1] = getLibtasVersion(fidDict[secondFilepath][2])
    fps_nums[0], fps_dens[0], varfpses[0] = getFPSConfig(fidDict[firstFilepath][2])
    fps_nums[1], fps_dens[1], varfpses[1] = getFPSConfig(fidDict[secondFilepath][2])

    outputStatus = -1
    # outputStatus indicates whether the output file is new, copied from file 1, or copied from file 2
    # 0: Output file was already created and should be overwritten
    # 1: Output file was copied from file 1
    # 2: Output file was copied from file 2

    # Check if output file exists, otherwise make a copy of the file with the newer version number
    if os.path.isfile(outputFilepath):
        # If it does exist, delete it. We will be making it ourselves.
        os.remove(outputFilepath)

        # fidDict.update(openltm(outputFilepath))
        # versions[2] = getLibtasVersion(fidDict[outputFilepath][2])
        # outputStatus = 0
        # if float(versions[2][2:]) < float(versions[1][2:]) and float(versions[2][2:]) < float(versions[0][2:]):
        #     # If the version of the output is lower than the version of both inputs, fall back on copying the newest input.
        #     # Find the file with the greatest version number,
        #     # simplifying the compare by assuming they all start with "1."
        #     # and have single digit minor/patch versions
        #     if float(versions[0][2:]) < float(versions[1][2:]): # Second file is newer version
        #         shutil.copyfile(secondFilepath, outputFilepath)
        #         fidDict.update(openltm(outputFilepath))
        #         versions[2] = versions[1]
        #         outputStatus = 2

        #     else: # First file is newer or the same version
        #         shutil.copyfile(firstFilepath, outputFilepath)
        #         fidDict.update(openltm(outputFilepath))
        #         versions[2] = versions[0]
        #         outputStatus = 1


    # Find the file with the greatest version number,
    # simplifying the compare by assuming they all start with "1."
    # and have single digit minor/patch versions
    if float(versions[0][2:]) < float(versions[1][2:]): # Second file is newer version
        shutil.copyfile(secondFilepath, outputFilepath)
        fidDict.update(openltm(outputFilepath))
        versions[2] = versions[1]
        outputStatus = 2

    else: # First file is newer or the same version
        shutil.copyfile(firstFilepath, outputFilepath)
        fidDict.update(openltm(outputFilepath))
        versions[2] = versions[0]
        outputStatus = 1

    # Add rerecord counts in preparation
    addRerecordCounts(fidDict[firstFilepath][2], fidDict[secondFilepath][2], fidDict[outputFilepath][2])

    # Now all the files are opened and the version numbers are known

    # Compare the default framerates and whether variable fps is on
    # For now assume an integer fps with den = 1. Otherwise the math gets complicated.
    inputFIDs = [0, 0, 0]
    with open(fidDict[firstFilepath][4]) as inputFIDs[0], open(fidDict[secondFilepath][4]) as inputFIDs[1], open(fidDict[outputFilepath][4], "w") as inputFIDs[2]:
        if fps_dens[0] == 1 and fps_dens[1] == 1:
            fps_nums[2] = fps_nums[0] # Make the new fps equal to the first file fps

            if varfpses[0] == "false" and varfpses[1] == "false" and fps_nums[0] == fps_nums[1]: # If no variable fps, same for output
                varfpses[2] = "false"
            else:
                varfpses[2] = "true"

            setFPSConfig(fidDict[outputFilepath][2], fps_nums[2], fps_dens[2], varfpses[2]) # Set the fps config options

            if versions[0] == versions[1]:
                # if the versions are all equal:
                inputFIDs[2].write(inputFIDs[0].read()) # The first file will always be at the base fps.
                if fps_nums[0] == fps_nums[1]:
                    # if the fpses are also equal
                    # inputFIDs[2].write(inputFIDs[0].read())
                    inputFIDs[2].write(inputFIDs[1].read())
                else: # if the second file is at a different fps
                    # if the fpses are not equal, use variable fps
                    # convertFPS(inputFIDs[0], fps_nums[0], fps_dens[0], inputFIDs[2], fps_nums[2], fps_dens[2])
                    convertFPS(inputFIDs[1], fps_nums[1], fps_dens[1], inputFIDs[2], fps_nums[2], fps_dens[2])

                    # for line in inputFIDs[0]:
                    #     # if the original fps matches the new fps, just copy everything as-is
                    #     if fps_nums[0] == fps_nums[2]:
                    #         inputFIDs[2].write(line)
                    #     # if it used variable fps, check if it's the first
                    #     elif "|T" in line:
                    #     # if it is the first, replace with original fps
                    #         lineSplitByFps = line.split("|T")
                    #         thisNum = int(lineSplitByFps[1].split(":")[0])

                    #         if varFpsUsed == False: # if it's the first case of variable fps
                    #             varFpsUsed = True
                    #             line = lineSplitByFps[0] + "|T" + str(fps_nums[0]) + ":" + str(fps_dens[0]) + "|\n" # Replace with original base fps
                    #         elif thisNum == fps_nums[2]:
                    #             line = lineSplitByFps[0]+ "|\n" # Remove variable fps
                    #         # Otherwise write the line as-is

                    #         inputFIDs[2].write(line)

                    #     else: # No variable fps but need to convert to variable fps
                    #         inputFIDs[2].write(line.strip("\n") + "T" + str(fps_nums[0]) + ":" + str(fps_dens[0]) + "|\n")

                    # for line in inputFIDs[1]:
                    #     # if the original fps matches the new fps, just copy everything as-is
                    #     if fps_nums[1] == fps_nums[2]:
                    #         inputFIDs[2].write(line)
                    #     # if it used variable fps, check if it's the first
                    #     elif "|T" in line:
                    #     # if it is the first, replace with original fps
                    #         lineSplitByFps = line.split("|T")
                    #         thisNum = int(lineSplitByFps[1].split(":")[0])

                    #         if varFpsUsed == False: # if it's the first case of variable fps
                    #             varFpsUsed = True
                    #             line = lineSplitByFps[0] + "|T" + str(fps_nums[1]) + ":" + str(fps_dens[1]) + "|\n" # Replace with original base fps
                    #         elif thisNum == fps_nums[2]:
                    #             line = lineSplitByFps[0]+ "|\n" # Remove variable fps
                    #         # Otherwise write the line as-is

                    #         inputFIDs[2].write(line)

                    #     else: # No variable fps but need to convert to variable fps
                    #         inputFIDs[2].write(line.strip("\n") + "T" + str(fps_nums[0]) + ":" + str(fps_dens[0]) + "|\n")


    # if the versions are different:
    # maybe don't worry about it and convert versions to latest using libTAS itself



    # finally, close all of the files
    closeltm(fidDict, merge = {firstFilepath:False, secondFilepath:False, outputFilepath:True})


def convertFPS(inputFID, inputNum, inputDen, outputFID, outputNum, outputDen, varFPS = False):
    """
    This function takes input and output information and writes the input into the output, changing fps if needed.

    Args:
        inputFID (file): FID for input file.
        inputNum (int): Input numerator.
        inputDen (int): Input denominator.
        outputFID (file): FID for output file. Inputs will be written wherever the current index is.
        outputNum (int): Output numerator.
        outputDen (int): Output denominator.
        varFPS (bool, optional): whether variable fps has been encountered yet.

    Returns:
        bool: varFPS, whether variable fps was used yet.

    """

    for line in inputFID:
        # # if the original fps matches the new fps, just copy everything as-is
        # if inputNum == outputNum:
        #     outputFID.write(line)
        # if it used variable fps, check if it's the first
        if "|T" in line:
        # if it is the first, replace with original fps
            lineSplitByFps = line.split("|T")
            thisNum = int(lineSplitByFps[1].split(":")[0])
            if thisNum == outputNum: # if the fps of this frame matches the new fps (can't match old fps or else it would not be variable fps)
                line = lineSplitByFps[0] + "|\n" # Remove variable fps
                # Otherwise write the line as-is

            outputFID.write(line)

        else: # No variable fps but need to convert to variable fps
            outputFID.write(line.strip("\n") + "T" + str(inputNum) + ":" + str(inputDen) + "|\n")
    return varFPS


def appendResetAndSeed(firstFilepath, secondFilepath):
    """
    Finds the initial seed using the start time from secondFilepath and appends a reset and extra time to the end of firstFilepath.
    This function is meant to be used in preparation for merging the two files.
    Keep in mind that mid-run seed resets will still need to be corrected.
    Assumes version 1.4.4. Assumes the last frame is the standard fps.

    Args:
        firstFilepath (str): Path to the first .ltm file.
        secondFilepath (str): Path to the second .ltm file.

    Returns:
        int: the new end time of the first file and the start time of the second file.

    """

    # First open up both files
    fidDict = openltm(firstFilepath)
    fidDict.update(openltm(secondFilepath))

    # Read the times: first file end time and second file start time
    startTime = getStartTime(fidDict[secondFilepath][2])
    endTime = getEndTime(fidDict[firstFilepath][2])

    # Read the first file fps
    num, den, varfps = getFPSConfig(fidDict[firstFilepath][2])

    # Set variable fps to true if it is not
    if varfps == False:
        setFPSConfig(fidDict[firstFilepath][2], variable_framerate = True)

    # Get the required seed
    state = randomizeMicrosState(startTime)

    # Search for the seed starting from endTime
    newEndTime = matchState(state, endTime)

    # newEndTime could be -1 if no seed was found within 1 second (probably means it's an error)
    if newEndTime < endTime:

        return

    # Calculate updated num and den for the final frame
    # Does this work for den other than 1? (probably)
    newNum = num * 1000000
    newDen = den * 1000000 + (num * (newEndTime - endTime))

    # Seek to final frame and change the framerate
    with open(fidDict[firstFilepath][4], "r+b") as firstInputFile:
        firstInputFile.seek(-1, 2) # Set file position one character before the end of the file
        lastLineStr = ""
        readChar = firstInputFile.read(1).decode("utf-8")

        while readChar != "\n": # Go until the beginning of the last line
            lastLineStr = readChar + lastLineStr # Prepend all the characters except the newline
            firstInputFile.seek(-2, 1)
            readChar = firstInputFile.read(1).decode("utf-8")
        firstInputFile.seek(-1, 1)
        # File position is now right at the beginning of last line, last line is stored in lastLineStr

        # This part assumes that the last frame is at the default fps, which it should be.
        lastLineStr += "T" + str(newNum) + ":" + str(newDen) + "|"

        #We are now at the beginning of the last line
        # Add an additional frame for the reset lasting 1ms
        # resetFrameStr = "|K|FR|T1000:1|"

        # firstInputFile.write((lastLineStr + "\n" + resetFrameStr + "\n").encode("utf-8"))
        # We don't really need a reset frame if it's going to reset anyway
        firstInputFile.write((lastLineStr + "\n").encode("utf-8"))

    # Close and merge
    closeltm(fidDict, merge={firstFilepath:True, secondFilepath:False})
    return startTime, newEndTime

def reseedGameReset(filePath, stateIndicesList, microsList, framesList):
    """
    Takes as input a file path to the ltm, a list of frames where rng is re-seeded,
    a list of the current microseconds for those frames, and a list of rng states corresponding to the frames list.
    Changes the fps of the frames in the list to make the new rng state into the desired one.

    Args:
        filePath (str): Path to the ltm file.
        stateIndicesList (list): A list of the desired state indices, from the synced TAS.
        microsList (list): A list of the microsecond values corresponding to the frames where rng is reseeded.
        framesList (list): A list of frames that are right before rng seed reseeding

    Returns:
        None.

    """

    # First open the ltm file
    fidDict = openltm(filePath)
    num, den, varfps = getFPSConfig(fidDict[filePath][2])

    # Set variable fps to true if it is not
    if varfps == False:
        setFPSConfig(fidDict[filePath][2], variable_framerate = True)

    microsAdditions = [0] * len(framesList)
    cumulativeMicrosAdditions = 0

    # Work out how many micros to add in each spot
    for i in range(len(framesList)):
        thisNewMicros = matchState(stateIndicesList[i], microsList[i] + cumulativeMicrosAdditions)
        microsAdditions[i] = thisNewMicros - microsList[i] - cumulativeMicrosAdditions
        cumulativeMicrosAdditions += microsAdditions[i]

    # Go through the lines and add new fps lines
    with open(fidDict[filePath][4], "r") as inputFile, open(fidDict[filePath][4] + "_new", "w") as outputFile:
        lineIndex = 0
        for line in inputFile:
            lineIndex += 1
            if lineIndex not in framesList:
                outputFile.write(line)
            else:
                listIndex = framesList.index(lineIndex)
                if "|T" in line: # variable fps, need to read what the fps is before changing it
                    lineSplitByFps = line.split("|T")
                    thisNum = int(lineSplitByFps[1].split(":")[0])
                    line = lineSplitByFps[0] + "|\n" # Remove the old variable fps from the line
                else: # base fps, no need to try to read the frame fps
                    thisNum = num
                newNum = thisNum * 1000000
                newDen = den * 1000000 + (thisNum * (microsAdditions[listIndex]))
                outputFile.write(line.strip("\n") + "T" + str(newNum) + ":" + str(newDen) + "|\n")
    os.remove(fidDict[filePath][4])
    os.rename(fidDict[filePath][4] + "_new", fidDict[filePath][4])

    # Close and merge
    closeltm(fidDict, merge=True)

def correctStatesFile(inputFilePath, startTime, outputFile = "seedsMicrosOutput.txt"):
    """
    Takes as input a path to states.txt, which is of the following format:
        state,microseconds,seed
    where the microseconds are an approximation for when the state occurred and the states are generated
    with the formula given in seedToState(), seeds.txt with one seed per line, the number of microseconds from the old start time,
    and the number of microseconds in the new start time when merged. Reads the states and microseconds and then replaces the
    microseconds with the exact correct microseconds value using the corresponding seed and start time.
    Frames are not possible to retrieve through this method so they must be retrieved in libTAS.

    Args:
        statesFilePath (string): A path to the states.txt file to be corrected
        startTime (int): Number of microseconds corresponding with the start time

    Returns:
        string: the output file path.

    """

    statesList = []
    microsList = []
    seedsList = []
    with open(inputFilePath, "r") as statesfid:
        for line in statesfid:
            statesList += [int(line.split(",")[0])]
            microsList += [int(line.split(",")[1])]
            seedsList += [int(line.split(",")[2])]

    with open(outputFile, "w") as outfid:
        for index in range(len(seedsList)):
            if index == 0: # Skip the first line
                continue
            elif index > 1: # Add the newline here so that there isn't an extra newline at the end
                outfid.write("\n")
            outfid.write(str(statesList[index]) + "," + str(matchSeed(seedsList[index], microsList[index] + startTime)) + "," + str(seedsList[index]))
            # Match seeds here because there are more seeds than states

    return outputFile

def statesFileToLists(statesFilePath, oldStartTime, newStartTime):
    """
    Takes as input a path to states.txt and outputs the lists expected by reseedGameReset().

    Args:
        statesFilePath (string): A path to the states.txt file with each line in the format state,micros,frame.

    Returns:
        list, list, list: states list, micros list, frames list.

    """
    statesList = []
    microsList = []
    framesList = []
    with open(statesFilePath) as fid:
        for line in fid:
            statesList += [int(line.split(",")[0])]
            microsList += [int(line.split(",")[1]) - oldStartTime + newStartTime]
            framesList += [int(line.split(",")[2])]

    return statesList, microsList, framesList

# Full merging process: (Note that source files will be modified in this process.)
#     1. Convert all files to libTAS version 1.4.4 and fps denominator of 1.
#     2. Run appendResetAndSeed() on the two files to be merged, storing the output (original start time and new start time of second file)
#     3. Use the states file mod to run the second file.
#     4. Run states.txt through correctStatesFile() using the normal start time of the second file.
#     5. Run the second file through libTAS again, either on the mod or vanilla.
#     6. At each point, find the exact microsecond value using libTAS's Elapsed Time.
#     7. If the exact Elapsed Time is missed, run matchSeed with the seed and a higher micros number until it's exactly hit.
#     8. In the file, replace the micros if needed and replace the seed (third entry on each line) with the frame count when you hit those micros.
#     9. Take the old start time, new start time, number of preceding frames, and the file path and feed into statesFileToLists().
#    10. Feed the filepath to the second ltm file and the output of statesFileToLists() to the reseedGameReset() function.
#    11. Feed the two filepaths and the output path to mergeLibtasFiles().
#    12. Repeat all steps as needed to merge all files.

def mergingProcess():
    """
    This is an interactive function that combines many of the other functions in this script into one process for merging ltm files.

    Returns:
        None.

    """

    repeatYN = "Y"

    print("This is the interactive ltm merging script, written by OceanBagel.\n\
\n\
This script is currently only for Undertale v1.001 Linux. Other version support may be coming in the future.\n\
Please make sure all files are from libTAS 1.4.4 and the fps denominator is always 1.\n\
You will need libTAS 1.4.4 and the states file mod to complete this process.\n\
Note that the input files will be modified, so make backups if needed.\n\n")

    while repeatYN == "Y":
        firstFilePath = input("Enter the path to the first file: ")
        secondFilePath = input("Enter the path to the second file: ")
        # numPrecedingFrames = int(input("Enter the length of the first file in frames: ")) + 1
        oldStartTime, newStartTime = appendResetAndSeed(firstFilePath, secondFilePath)

        print("\nBefore continuing, complete the following step:\n\
\t* Use the states file mod to run the second file.\n\
When you have finished this step, enter the file path to the states.txt file below.")
        statesFilePath = input("Enter the path to the states.txt file: ")
        statesOutputFilePath = input("Enter a path for the new states.txt file: ")
        correctStatesFile(statesFilePath, oldStartTime, statesOutputFilePath)

        print("\nBefore continuing, complete the following steps:\n\
\t* Run the second ltm file through libTAS again, either on the mod or vanilla.\n\
\t* At each point from the output states.txt, find the exact microsecond value (second entry on each line) using libTAS's Elapsed Time.\n\
\t* If the exact Elapsed Time is missed, enter the seed and the next value of microseconds below.\n\
\t* In the file, replace the micros (second entry on each line) if needed\n\
\t  and replace the seed (third entry on each line) with the frame count when you hit those micros.\n\
\t* Press Enter without typing anything below to continue to the next step.")
        while True: # Loop as long as needed until a non-integer is entered
            try:
                seedToSearch = int(input("Enter the seed to search (third entry) or enter nothing to move to the next step: "))
                microsToSearch = int(input("Enter the micros to search (Elapsed Time): "))
            except ValueError: # A non-integer was entered so move to the next step
                break
            print("Your new micros value is {}.\n".format(matchSeed(seedToSearch, microsToSearch)))

        reseedGameReset(secondFilePath, *statesFileToLists(statesOutputFilePath, oldStartTime, newStartTime)) # An extra 1000 micros due to restart frame

        outputFilePath = input("\nEnter the output merged ltm file path: ")
        mergeLibtasFiles(firstFilePath, secondFilePath, outputFilePath)

        repeatYN = input("\nMerge completed successfully! Enter Y to perform the merge process again or anything else to exit: ")
