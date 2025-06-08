-- Safari Bookmarks Import Script
-- This script uses Safari's built-in "Import From Browser" feature
-- to import bookmarks directly from an HTML file.
-- It searches for HTML files in the step5sync2safari directory and navigates directly to them.

on run
	-- Confirm with the user before proceeding
	set dialogText to "This script will import bookmarks from an HTML file into Safari using Safari's built-in import feature." & return & return & "This may add new bookmarks to Safari. Do you want to continue?"
	set userResponse to display dialog dialogText buttons {"Cancel", "Import"} default button "Import" with title "Confirm HTML Import" with icon note
	
	if button returned of userResponse is "Cancel" then
		return "User cancelled operation"
	end if
	
	-- Get system language to use correct menu item names
	set systemLanguage to do shell script "defaults read -g AppleLocale | cut -d '_' -f 1"
	
	set safariFileMenu to "File"
	set safariImportMenuItem to "Import From"
	set safariImportBrowserMenuItem to "Import Browsing Data from File or Folder…"
	
	if systemLanguage is "zh" then
		set safariFileMenu to "文件"
		set safariImportMenuItem to "导入自"
		set safariImportBrowserMenuItem to "从文件或文件夹导入浏览数据…"
	end if
	
	try
		-- Search for HTML file in step5sync2safari directory and get absolute path
		set currentDir to (do shell script "pwd")
		set searchPath to currentDir & "/step5sync2safari"
		set htmlFilePath to (do shell script "find " & quoted form of searchPath & " -name '*.html' | head -1")
		
		-- Debug: log the path for troubleshooting
		log "Current directory: " & currentDir
		log "Search path: " & searchPath
		log "Found HTML file: " & htmlFilePath
		
		if htmlFilePath is "" then
			error "No HTML file found in step5sync2safari directory"
		end if
		
		-- Switch to English input method first
		tell application "System Events"
			key code 49 using {control down} -- Ctrl+Space to switch input method
			delay 1
		end tell
		
		-- Perform the import using System Events
		tell application "Safari"
			activate
			delay 1 -- Give Safari time to activate
		end tell
		
		tell application "System Events"
			tell process "Safari"
				set frontmost to true
				delay 0.5
				
				-- Click File menu
				click menu safariFileMenu of menu bar 1
				delay 1
				
				-- Click Import Browsing Data from File or Folder directly
				click menu item safariImportBrowserMenuItem of menu safariFileMenu of menu bar 1
				delay 2
				
				-- This will open a file selection dialog
				tell window 1
					-- Use keystroke to navigate to the directory containing the HTML file
					key code 7 using {command down} -- Cmd+G for Go to Folder
					delay 2 -- Wait for Go to Folder dialog to appear
					
					-- Clear any existing text and type the directory path
					key code 0 using {command down} -- Cmd+A to select all
					delay 0.5
					set htmlDir to currentDir & "/step5sync2safari"
					-- Debug: log the directory path we're about to type
					log "Directory path to type: " & htmlDir
					-- Type character by character to avoid substitution
					repeat with i from 1 to length of htmlDir
						keystroke (character i of htmlDir)
						delay 0.1
					end repeat
					delay 1
					key code 36 -- Enter to navigate to the directory
					delay 3 -- Wait for navigation to complete
					
					-- Now select the HTML file by typing its name character by character
					repeat with i from 1 to length of "safari_bookmarks"
						keystroke (character i of "safari_bookmarks")
						delay 0.1
					end repeat
					delay 1
					key code 36 -- Enter to select the file
					delay 2
					
					-- Click Import button to complete the import
					try
						click button "Import" of window 1
					on error
						-- If Import button not found, try pressing Enter or Space
						key code 49 -- Space bar
					end try
					delay 3
					
					display dialog "Bookmarks imported successfully from HTML file!" buttons {"OK"} default button 1 with title "Import Successful" with icon note
					return "Import successful"
				end tell
			end tell
			end tell
		
	on error e number n
		-- If any error occurs during the process, display an error and manual instructions
		set manualInstruction to "Automatic import failed: " & e & return & return & "Please import manually:" & return & "1. Open Safari." & return & "2. Go to '" & safariFileMenu & "' > '" & safariImportMenuItem & "' > '" & safariImportBrowserMenuItem & "'." & return & "3. Navigate to: " & htmlFilePath & return & "4. Select the HTML file and click 'Import'."
		display dialog manualInstruction buttons {"OK"} default button 1 with title "Import Failed" with icon stop
		return "Import failed: " & e
	end try
end run