import os
import datetime
import tempfile
import json
from shutil import copyfile


def start():
    difficultyNameList = ["ExpertPlus.json", "Expert.json", "Hard.json", "Normal.json", "Easy.json"]
    print("Starting Conversion")
    baseDir = "E:/SteamLibrary/steamapps/common/Beat Saber"
    print(f"BeatSaber Install Dir: {baseDir}")
    print("Moving to CustomSongs")
    customSongsDir = f"{baseDir}/CustomSongs"
    customLevelsDir = f"{baseDir}/Beat Saber_Data/CustomLevels"
    os.chdir(customSongsDir)    
    print(f"I'm here what the fuck are you gonna do: {os.getcwd()}")

    #Get all the subdirs
    songList = os.listdir(".")
    #Remove shit we don't care about
    try:
        songList = list(dict.fromkeys(songList)) #remove dupes
    except Exception:
        pass   
    try:        
        songList.remove("tmp") #cache is always there, tmp only if we fuck up
    except Exception:
        pass
    try:        
        songList.remove(".cache") #cache is always there, tmp only if we fuck up
    except Exception:
        pass
    try:
        songList = songList[:] = [x for x in songList if ".exe" not in x] # signs of my messy working directory
    except Exception:
        pass
    
    #Info
    print(f"Found: {len(songList)} songs!")
    print("Creating Custom Levels directory")
    try:
        os.mkdir(customLevelsDir)
    except Exception as e:
        pass

    errCount = 0
    errLog = ""
    startTime = datetime.datetime.now()
    #In we go
    for count, value in enumerate(songList):
        print(f"Processing Song #{count}: {value}")
        songDir = f"{customSongsDir}/{value}"
        print(f"SongDir: {songDir}")
        os.chdir(songDir)
        #Get files
        songFiles = os.listdir()
        print("Files found in songdir:")
        print(songFiles)
        #Make the new song dir in temp
        try:
            newSongDir = f"{customLevelsDir}/{value}"
            print(f"New Song Dir: {newSongDir}")
            os.mkdir(newSongDir)
        except Exception as e:
            pass

        trackName = ""
        picName = ""
        #Begin processing
        #need trackname and image name first because im a fucking dummy
        for item in songFiles:
            print(f"Current Item: {item}")
            if item.endswith(".ogg"):
                try:
                    print(f"Renaming and moving: {item}")
                    trackName = item.replace(".ogg", ".egg")                    
                    src = f"{songDir}/{item}"
                    dest = f"{customLevelsDir}/{value}/{trackName}"
                    copyfile(src,dest)

                except Exception as e:
                    errCount = errCount + 1
                    errLog += f"Error on item: {item} in {songDir} - {repr(e)}\n"
            
            #Move cover pic
            elif item.endswith(".jpg") or item.endswith(".jpeg") or item.endswith(".png") or item.endswith(".bmp"):
                try:
                    print(f"Moving: {item}")
                    picName = item
                    src = f"{songDir}/{item}"
                    dest = f"{customLevelsDir}/{value}/{item}"
                    copyfile(src,dest)

                except Exception as e:
                    errCount = errCount + 1
                    errLog += f"Error on item: {item} in {songDir} - {repr(e)}\n"

            else:
                #ignore files we dont care about
                pass
        
        #Now we can process info and difficulty
        for item in songFiles:
            # Convert info.json to info.dat
            if item == "info.json":
                try:
                    infoPath = f"{songDir}/{item}" 
                    print("Converting info.json to info.dat")
                    #print(f"Info File: {infoPath}")
                    with open(infoPath, 'r') as info:
                        contents = json.loads(info.read())
                        #print(contents)

                        newFormat = {}
                        newFormat["_version"] = "2.0.0"
                        newFormat["_songName"] = contents["songName"]
                        newFormat["_songSubName"] = "JoeFix"
                        newFormat["_songAuthorName"] = ""
                        newFormat["_levelAuthorName"] = contents["authorName"]
                        newFormat["_beatsPerMinute"] = contents["beatsPerMinute"]
                        newFormat["_songTimeOffset"] = 0
                        newFormat["_shuffle"] = 0
                        newFormat["_shufflePeriod"] = 0.5
                        newFormat["_previewStartTime"] = contents["previewStartTime"]
                        newFormat["_previewDuration"] = contents["previewDuration"]
                        newFormat["_songFilename"] = trackName
                        newFormat["_coverImageFilename"] = picName
                        newFormat["_environmentName"] = contents["environmentName"]
                        newFormat["_customData"] =  {
                            "_contributors":[],
                            "_customEnvironment":"",
                            "_customEnvironmentHash":""
                        }
                        diffLevels = []
                        counter = 1
                        for difficultyLevel in contents["difficultyLevels"]:
                            level = {}
                            level["_difficulty"] = difficultyLevel["difficulty"]			
                            level["_difficultyRank"] = difficultyLevel["difficultyRank"]
                            level["_beatmapFilename"] = difficultyLevel["jsonPath"].replace(".json", ".dat")
                            level["_noteJumpMovementSpeed"] = 16
                            level["_noteJumpStartBeatOffset"] = 0
                            level[ "_customData"] = {  
                                "_difficultyLabel": "",
                                "_editorOffset": difficultyLevel["offset"] if "offset" in difficultyLevel else 0,
                                "_editorOldOffset": difficultyLevel["oldOffset"] if "oldOffset" in difficultyLevel else 0,
                                "_warnings": [],
                                "_information": [],
                                "_suggestions": [],
                                "_requirements": []
                            }
                            diffLevels.append(level)
                            counter = counter+1

                        newFormat["_difficultyBeatmapSets"] = [
                            {
                                "_beatmapCharacteristicName": "Standard",
                                "_difficultyBeatmaps": diffLevels
                            }
                        ]

                        #Go to new song dir and spit out the dat file
                        os.chdir(newSongDir)
                        with open('info.dat', 'w') as outfile:
                            json.dump(newFormat, outfile, separators=(',', ':'), indent=2)

                except Exception as e:
                    errCount = errCount + 1
                    errLog += f"Error on item: {item} in {songDir} - {repr(e)}\n"

            elif item in difficultyNameList:
                print(f"Converting Difficulty Map file: {item}")
                try:
                    beatFilePath = f"{songDir}/{item}"
                    with open(beatFilePath, 'r') as info:
                        contents = json.loads(info.read())
                        newFormat = {}

                        newFormat["_version"] = "2.0.0"
                        newFormat["_time"] = "0"
                        newFormat["_BPMChanges"] = []

                        newFormat["_events"] = contents["_events"]
                        newFormat["_notes"] = contents["_notes"]
                        newFormat["_notes"] = contents["_notes"]
                        newFormat["_bookmarks"] = []

                        os.chdir(newSongDir)
                        fileName = item.replace(".json", ".dat")

                        with open(f'{fileName}', 'w') as outfile:
                            json.dump(newFormat, outfile, separators=(',', ':'))

                except Exception as e:
                    errCount = errCount + 1
                    errLog += f"Error on item: {item} in {songDir} - {repr(e)}\n"
            
            else:
                #ignore files we dont care about
                pass
    
    endTime = datetime.datetime.now()
    totalTime = endTime - startTime
    print(f"Finished Converting {len(songList)} songs with {errCount} errors in {totalTime.total_seconds()} seconds")
    if errCount > 0:
        print(errLog)
    print("kthxbai")


if __name__ == "__main__":
    start()
