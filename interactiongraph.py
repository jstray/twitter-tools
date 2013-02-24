# build a directed graph, such that
# graph[(user1, user2)] = how many times user2 replied/retweeted/mentioned user 1 

def build_interaction_graph(lines)

    edges = {}

    for line in lines:
        t = json.loads(line)

        user = t['user']['screen_name']
        otheruser = None

        if 'retweeted_status' in t:
            otheruser = t['retweeted_status']['user']['screen_name']
            action = "retweeted"

        elif t['in_reply_to_screen_name'] != None:
            otheruser = t['in_reply_to_screen_name']
            action = "replied to"

        elif len(t['entities']['user_mentions'])>0:
            otheruser = t['entities']['user_mentions'][0]['screen_name']
            action = "mentioned"

        if user != None and otheruser != None:
            users.add(user)
            users.add(otheruser)
            edges[(user,otheruser)] = edges.get((otheruser,user), 0) + 1

    return edges


