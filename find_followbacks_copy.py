import argparse
import subprocess

try:
    import tweepy
except ImportError:
    print('Missing Tweepy!. Try installing tweepy and try again.')

def check_followers_to_following_ration(user: tweepy.models.User, value: float) -> bool:
    """Given a tweepy user model and float value, calculate a 
    variance in followers to following, and see if they are 
    within that given percentage. 

    For example, if the given value is .2, and a user has 1000 
    followers and is following 800, True is returned because the 
    smaller of the two values can fall between 800-1200.
    """
    num_followers = user.followers_count
    num_following = user.friends_count
    smaller_num, bigger_num = sorted([num_following, num_followers])
    variance = bigger_num * value
    return (bigger_num-variance) <= smaller_num <= (bigger_num+variance)

def get_user_info(user: tweepy.models.User) -> list:
    """Given a tweepy user model, returns a list of string
    data about the account such as number of name, description, 
    number of tweets, etc, as well as the most recent tweets.
    """
    user_data = [
        f"Created at: {user.created_at.month}-{user.created_at.year}",
        f"Name: {user.name}",
        f"Description: {user.description}",
        f"Number of Tweets: {user.statuses_count}",
        f"Followers: {str(user.followers_count)}",
        f"Following: {str(user.friends_count)}",
        f"Protected: {user.protected}"
    ]
    tweets = ["Latest Tweets: {}".format(
        '\n'.join(get_user_tweets(user.screen_name)))]
    return user_data + tweets

def get_user_tweets(screen_name: str, n_tweets=3) -> list:
    """Given a Twitter screen name, return a list of the 
    last n tweets for the user.
    """
    tweet_data = api.user_timeline(screen_name=screen_name, count=n_tweets)
    return [tweet.text for tweet in tweet_data]

def follow_user(screen_name: str) -> None:
    """Given a Twitter screen name, will follow that user
    and enable follow notifications.
    """
    api.create_friendship(screen_name=screen_name, follow=True)

def search(query: str, max_tweets=100) -> tweepy.models.SearchResults:
    """Given a search string, queries twitter and returns 
    100 results.
    """
    searched_tweets = []
    last_id = -1
    while len(searched_tweets) < max_tweets:
        count = max_tweets - len(searched_tweets)
        try:
            new_tweets = api.search(q=query, count=count, max_id=str(last_id - 1))
            if not new_tweets:
                break
            searched_tweets.extend(new_tweets)
            last_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            break
    users = [tweet.user for tweet in searched_tweets]
    return users

def main():
    """The main function."""

    # My user information
    my_user = api.me()
    my_friends = api.friends_ids(my_user.screen_name)
    my_followers = api.followers_ids(my_user.screen_name)
    
    # Initial search of the users based on a query keyword
    print(f'[*] Searching {tweets} tweets using the query: "{query}"')
    users = search(query)
    
    # Empty list to populate potential candidates to follow.
    candidates = []
    
    # Only include users that I don't have a relationship with.
    print('[*] Checking the follower/following status for each user.')    
    for user in users:
        if user.id in my_friends or user.id in my_followers:
            continue
        candidates.append(user)

    # Only include users that include the proper follower/following ratio.
    print(f'[*] Checking user ratio of followers to following for {len(candidates)} users.')
    candidates = [user for user in candidates if check_followers_to_following_ration(user, ratio)]

    # Gather data about these users and last n tweets.
    print(f"[*] Gathering information about {len(candidates)} users that likely followback.")
    candidates_user_data = {}
    for candidate in candidates:
        candidates_user_data[candidate.screen_name] = get_user_info(candidate)

    # Review data and see if you want to follow.
    for user in candidates_user_data:

        # Clears the screen to make things easier to read.
        subprocess.call('cls||clear', shell=True, stderr=subprocess.DEVNULL)

        print('[+]',user)
        print('\n'.join(candidates_user_data.get(user)))
        ans = input("\n[+] Would you like to follow? Press y if yes, or any "
              "other key to continue to the next user.\n")
        if ans.lower().startswith('y'):
            follow_user(user)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose",
                        help="Increase output verbosity", 
                        action="store_true")
    parser.add_argument("-q", "--query",
                        help="Add a search term to limit results.")
    parser.add_argument("-r", "--ratio",
                        type=int,
                        help=("Specify an integer that indicates "
                              "ratio of followers to following."))
    parser.add_argument("-t", "--tweets",
                        type=int,
                        choices=range(1,1000),
                        metavar="[1-1000]",
                        help=("Specify the number of tweets to search "
                              "to find users. Default is 100. This  can take ."
                              "a long time to run depending on number specified."))
    args = parser.parse_args()

    # Add your keys here
    consumer_key = ''
    consumer_secret = ''
    access_token = ''
    access_token_secret = ''

    # Specify a default query and ratio if you want
    query = args.query if args.query else 'infosec'
    ratio = (args.ratio if args.ratio else 30) *.01 # Convert to percentage
    tweets = args.tweets if args.tweets else 100

    # Authorizing access
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    main()