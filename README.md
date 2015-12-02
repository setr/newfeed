# I HATE MOBILE WEB BROWSING
## BUT I LIKE MY RSS READER

This is meant to fetch the rss feed, then go to each article and grab the full textual content, and plug it back to the rss feed.

Finally, the new feed gets hosted under setr.github.io/newfeed/, which can be subscribed to on my RSS reader.

Thus, I obtain everything, have auto-fetching and caching from my reader, and don't have to worry about ads and whatever other garbage they want to visit their site for.

I think for the most part adding new feeds should be trivial, you really just need to make sure readability parses correctly (toss in some more negative keywords) and nothing fucks up with the regex. 

Specifically, I'm assuming there'll always be a `<description><![CDATA[.*?]]></description>` tag to just drop the content into.

Alternatively, if RSS's turn out to be quite varied, I'll just build a new RSS template from scratch and drop feeds into it


## Feeds

[The New Yorker](setr.github.io/newfeed/finalyorker.rss)

[Nautilus](setr.github.io/newfeed/finalnaut.rss)

## Requirements

[python-readability](https://github.com/buriy/python-readability)
