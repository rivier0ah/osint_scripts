'''
Gets Insta username and display name from userId
Written by @rivier0ah, MIT-licensed.
'''
import sys, time, csv, argparse, json, requests

sessionId = None

def userIdToUserProfile(userid):
    headers = {'User-Agent': 'Instagram 64.0.0.14.96',}
    cookies = {'sessionid': sessionId}
    r = requests.get(
        f'https://i.instagram.com/api/v1/users/{userid}/info/',
        headers=headers, cookies=cookies)

    if r.status_code == 404:
        return False

    j = json.loads(r.text)

    if j.get("status") != 'ok':
        print(f"[x] Rate limit reached, stuck on: {userid}\n[x] Now waiting for 340sec..\n")
        time.sleep(340) #May be too much?
        return userIdToUserProfile(userid)
    try:
        return (j['user']['username'], j['user']['full_name'])
    except IndexError:
        return False


def main():
    parser = argparse.ArgumentParser(prog='InstaTracker.py')

    parser.add_argument('-i', '--id', action='store', dest='userId',
                        help='Instagram userID to look up. If not provided, expects input from stdin.', type=int)
    parser.add_argument('-s', '--session-id', action='store', dest='sessionId',
                        help='Set sessionId to access Insta\'s API', type=str, required=True)
    parser.add_argument('-c', '--csv', action='store', dest='file',
                        help='File in which to write CSV-formatted userId, username and displayname',
                        type=str)
    args = parser.parse_args()

    global sessionId
    sessionId = args.sessionId

    if not args.userId:
        with open(args.file, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)

            for line in sys.stdin:
                userId = line[:-1]
                userId = userId.split(" ", 1)
                userId = userId[0]
                fetchResult = userIdToUserProfile(userId) or ["",""]
                csvwriter.writerow([userId, *fetchResult])
                print(f"{userId},{fetchResult[0]},{fetchResult[1]}" if fetchResult else f"{userId},,")
                csvfile.flush()
                time.sleep(1.8) #This has not been calibrated, but as of Feb. 2022, does not trigger rate-limiting even after 1h of continuous requests
    else:
        fetchResult = userIdToUserProfile(args.userId)
        if not fetchResult:
            print('[-] UserID does not exist')
        else:
            print(f"[+] Username: {fetchResult[0]}")
            print(f"[+] Display name: {fetchResult[1]}")

if __name__ == '__main__':
    main()
