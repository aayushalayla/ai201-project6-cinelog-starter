# PR Response Doc — CineLog Watchlist Feature

## AI Usage

## Comment 1 — Rename
**What I did:**
I renamed save_to_watchlist() to add_to_watchlist() in services/watchlist_service.py so the function follows CineLog’s existing verb-to-noun naming convention. I also updated the import and function call in routes/watchlist/watchlist.py.

**How I verified:**
I ran a project-wide grep search for save_to_watchlist, excluding generated cache directories, and confirmed that no references to the old function name remained. I then ran the full test suite with pytest tests/ -v to confirm the rename did not break existing functionality.

## Comment 2 — Deduplication

**What I did:** 
Added a query in `add_to_watchlist()` that checks whether a `WatchlistEntry` already exists with the same `user_id` and `film_id`. If a duplicate exists, the function raises `AlreadyInWatchlistError` instead of creating another entry. I followed the existing pattern in `add_to_collection()`.

**How I verified:**
I ran the complete test suite with `pytest tests/ -v` and confirmed the existing tests still passed. I also verified that the query checks both `user_id` and `film_id`, allowing different users to add the same film while preventing duplicates for one user.

## Comment 3 — Missing test

**What I did:**
I created tests/test_watchlist.py and added a test confirming that add_to_watchlist() raises FilmNotFoundError when given a film UUID that does not exist. I followed the fixture, in-memory database, and exception assertion pattern used by test_add_to_collection_nonexistent_film_raises() in tests/test_collection.py.

**How I verified:**
I ran pytest tests/test_watchlist.py -v to verify the new test independently. I then ran pytest tests/ -v and confirmed that the complete test suite passed.

## Comment 4 — Default visibility

**My position:**
I would keep public=True as the current default because CineLog is designed as a community film-tracking application, and visible watchlists support film discovery and interaction between users.

**Reasoning:**
A public default reduces friction for the application’s social features. Users can add a film and have it immediately appear as part of their visible profile without needing an additional configuration step. Additionally,the current add endpoint accepts only film_id, so changing the default to private would make every new watchlist entry invisible with no way for the caller to make it public. This is consistent with treating a watchlist as a recommendation or expression of taste. Because there is no personal data that is being compromised, this allows logs to effectively display users entries. 

**Tradeoff acknowledged:**
Perhaps an additional parameter could be added to allow users to add entries privately. 

## Comment 5 — Sort order
**My position:**
I would sort the watchlist by date_added ascending, so the films that have been waiting longest appear first.

**Reasoning:**
Because a watchlist is a backlog of films the user intends to watch, 
showing the oldest entries gives a list a queue like function and helps users 
see films they have been meaning to watch. 

**Engagement with reviewer's point:**
I agree with the reviewer that chronological order is more meaningful than alphabetical order, but I would use the opposite chronological direction. Newest-first is useful for an activity feed, while oldest-first is more useful for managing an unfinished watchlist. The tradeoff is that recently added films may require scrolling, so a future interface should allow users to choose between oldest, newest, and alphabetical sorting but this would incentivize going through films that a user has been meaning to watch. 

## Comment 6 — Rebase
**What conflicted:**
The rebase caused an add/add conflict in .gitignore because both main and my feature branch had added the file. The contents were basically the same, just arranged differently, so I kept one combined version. After the rebase finished, the tests revealed another problem that Git did not flag as a conflict: WatchlistEntry had disappeared from models.py.
**How I resolved it:**
 I compared both versions and kept the combined set of ignore rules, including the virtual environment, Python cache files, pytest cache, database files, and local instance directory.
 I also restored WatchlistEntry in models.py while adapting it to the UUID refactor on main. In particular, I changed film_id from the feature branch’s former integer foreign key to db.String(36), matching the UUID-based Film.id. I also updated the watchlist service and route documentation so they describe film_id as a UUID string rather than an integer.

**How I verified no conflict remains:**
I ran the full test suite with pytest tests/ -v and confirmed that both the collection and watchlist tests passed. I also checked git status to make sure the working tree was clean and ran git log --merges upstream/main..HEAD to confirm that the branch had no merge commits.

## PR Description
This PR finishes the watchlist feature and addresses all six review comments.

The watchlist now uses the same naming and validation patterns as the collection service. I renamed `save_to_watchlist()` to `add_to_watchlist()`, added duplicate protection, added coverage for nonexistent film IDs, rebased the branch onto the UUID-based version of `main`, and restored `WatchlistEntry` using UUID foreign keys.

## AI Usage
I used AI to help me understand the existing collection-service pattern, especially how `add_to_collection()` checks for duplicate entries and handles nonexistent films. I also used it to troubleshoot the rebase, review my conventional commit messages, and stress-test my reasoning about watchlist visibility and sort order. I verified the suggestions against the actual code and test results before applying them.

## Design decisions

### Visibility

I kept `public=True` as the default for this PR. CineLog treats the watchlist as part of a user’s film profile, and the current endpoint only accepts `film_id`. Changing the default to private would make every new entry invisible without giving the caller any way to make it public.

The privacy concern is still valid, so a better follow-up would be to let the endpoint accept an explicit `public` value.

### Sort order

I changed the watchlist to sort by `date_added` ascending, so the films that have been waiting longest appear first.

I chose this because a watchlist functions more like a backlog than an activity feed. Alphabetical order ignores the history of the list, while newest-first keeps rewarding recent additions and lets older films disappear indefinitely. Oldest-first gives the watchlist a simple queue-like behavior.

A stronger long-term design would support user-defined ordering through a `position` or `priority` field.
