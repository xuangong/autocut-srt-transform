import os
import re

g_n = 5 # Number of seconds to add to each subtitle

def convert_to_srt(file_content):
    lines = file_content.split('\n')
    srt_entry = ""
    srt_content = ""
    previous_end_time = None
    previous_text = None
    previous_duration_seconds = None
    index = 1

    for line in lines:
        if not re.match(r"- \[ \] \[\d+,\d{2}:\d{2}\] .+", line):
            continue

        parts = line.split('] ')
        index_and_time = parts[1].split(' ')[0].replace('[', '')
        subtitle_text = ' '.join(parts[2].split(' ')[1:]).strip()

        # Skip '< No Speech >' subtitles
        if subtitle_text == "< No Speech >":
            continue

        _, time = index_and_time.split(',')[0], index_and_time.split(',')[1]
        if len(time.split(':')) > 2:
            [time_hours, time_minutes, time_seconds] = time.split(':')
        else:
            time_hours, time_minutes, time_seconds = "00", time.split(':')[0], time.split(':')[1]

        
        # Set start time as previous end time if available, else use current time
        start_time = f"{time_hours}:{time_minutes}:{time_seconds},000"
        
        # Calculating the duration in seconds
        duration_seconds = int(time_hours) * 60 * 60 + int(time_minutes) * 60 + int(time_seconds)

        if previous_duration_seconds is not None:
            if duration_seconds - previous_duration_seconds <= g_n:
                srt_entry = f"{index}\n{previous_end_time} --> {start_time}\n{previous_text}\n\n"
            else:
                end_minutes, end_seconds = divmod(previous_duration_seconds + 5, 60)
                end_hours, end_minutes = divmod(end_minutes, 60)
                end_time = f"{str(end_hours).zfill(2)}:{str(end_minutes).zfill(2)}:{str(end_seconds).zfill(2)},000"

                if previous_end_time is not None:
                    srt_entry = f"{index}\n{previous_end_time} --> {end_time}\n{previous_text}\n\n"
                else:
                    srt_entry = f"{index}\n{start_time} --> {end_time}\n{subtitle_text}\n\n"
                
        end_minutes, end_seconds = divmod(duration_seconds, 60)
        end_hours, end_minutes = divmod(end_minutes, 60)
        end_time = f"{str(end_hours).zfill(2)}:{str(end_minutes).zfill(2)}:{str(end_seconds).zfill(2)},000"

        index += 1
        srt_content += srt_entry

        previous_end_time = end_time
        previous_text = subtitle_text
        previous_duration_seconds = duration_seconds

    index += 1
    end_minutes, end_seconds = divmod(previous_duration_seconds + g_n, 60)
    end_hours, end_minutes = divmod(end_minutes, 60)
    end_time = f"{end_hours}:{str(end_minutes).zfill(2)}:{str(end_seconds).zfill(2)},000"
    srt_entry = f"{index}\n{previous_end_time} --> {end_time}\n{previous_text}\n\n"
    srt_content += srt_entry

    return srt_content.strip()

for filename in os.listdir('.'):
    if filename.endswith('.md'):
        with open(filename, 'r') as f:
            file_content = f.read()
        print(f"Converting {filename} to srt...")
        srt_content = convert_to_srt(file_content)
        srt_filename = filename.replace('.md', '.srt')
        with open(srt_filename, 'w') as f:
            f.write(srt_content)