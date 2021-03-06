"""Tests for mission endpoints."""


import flask
import json
import unittest

import backend
import harness


class QuestTest(harness.TestHarness):
    """Tests for quest endpoints."""

    @harness.with_sess(user_id=1)
    def test_crud(self):
        """Basic CRUD tests."""
        # no quest yet, so 404
        resp = self.app.get("/v1/quest/1")
        self.assertEqual(resp.status_code, 404)

        # create a user, some missions, and some quests
        harness.create_user(name="snakes")
        harness.create_user(name="rakes")

        resp = self.post_json(
                self.url_for(backend.quest_views.QuestList),
                {"name": "mouse", "summary": "nip",
                    "inquiry_questions": ['a', 'b']})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.data), {
            "name": "mouse", "summary": "nip", "inquiry_questions": ["a", "b"],
            "icon_url": None, "video_links": [],
            "id": 1, "url": "/v1/quests/1", 'tags': [],
            "pbl_description": None, "mentor_guide": None,
            "min_grade_level": None, "max_grade_level": None,
            "hours_required": None, "minutes_required": None,
            "creator_id": 1, "creator_url": "/v1/users/1"})
        self.assertEqual(resp.status_code, 200)
        resp = self.post_json(
                self.url_for(backend.quest_views.QuestList),
                {"name": "blouse", "summary": "blip"})
        self.assertEqual(resp.status_code, 200)

        # create this one as a different user
        self.update_session(user_id=2)
        resp = self.post_json(
                self.url_for(backend.quest_views.QuestList),
                {"name": "house", "summary": "snip", "icon_url": "blue"})
        self.assertEqual(resp.status_code, 200)
        self.update_session(user_id=1)

        # and get it back
        resp = self.app.get("/v1/quests/1")
        self.assertEqual(json.loads(resp.data), {
            'creator_id': 1,
            'creator_url': '/v1/users/1',
            'summary': 'nip',
            'icon_url': None,
            "inquiry_questions": ["a", "b"], 'tags': [],
            "pbl_description": None, "mentor_guide": None,
            "min_grade_level": None, "max_grade_level": None,
            "hours_required": None, "minutes_required": None,
            'id': 1,
            'video_links': [],
            'url': '/v1/quests/1',
            'name': 'mouse'})

        # edit
        resp = self.put_json('/v1/quests/1', {
            'summary': 'nip', 'name': 'mouse', 'icon_url': 'rubber',
            "pbl_description": 'p', "mentor_guide": 'g',
            "min_grade_level": 1, "max_grade_level": 2,
            "hours_required": 3, "minutes_required": 4,
            "video_links": ['snakes.mp4', 'ladders.mp4'], 'tags': [],
            'inquiry_questions': ['b', 'c', 'd']})
        self.assertEqual(resp.status_code, 200)

        # non-required values may be None
        resp = self.put_json('/v1/quests/1', {
            'summary': 'nip', 'name': 'mouse', 'icon_url': 'rubber',
            "pbl_description": 'p', "mentor_guide": None,
            "min_grade_level": 1, "max_grade_level": None,
            "hours_required": 3, "minutes_required": 4,
            "video_links": ['snakes.mp4', 'ladders.mp4'], 'tags': [],
            'inquiry_questions': ['b', 'c', 'd']})
        self.assertEqual(resp.status_code, 200)

        # and get it back
        resp = self.app.get("/v1/quests/1")
        self.assertEqual(json.loads(resp.data), {
            'creator_id': 1,
            'creator_url': '/v1/users/1',
            'summary': 'nip',
            "pbl_description": 'p', "mentor_guide": None,
            "min_grade_level": 1, "max_grade_level": None,
            "hours_required": 3, "minutes_required": 4,
            'icon_url': 'rubber',
            "video_links": ['snakes.mp4', 'ladders.mp4'],
            "inquiry_questions": ["b", "c", "d"], 'tags': [],
            'id': 1,
            'url': '/v1/quests/1',
            'name': 'mouse'})

        # list them
        resp = self.app.get(self.url_for(
            backend.quest_views.QuestUserList, user_id=1))
        self.assertItemsEqual(json.loads(resp.data)['quests'], [
            {'creator_id': 1, 'summary': 'nip', 'icon_url': 'rubber',
                'creator_url': '/v1/users/1',
                "inquiry_questions": ["b", "c", "d"], 'tags': [],
                "pbl_description": 'p', "mentor_guide": None,
                "min_grade_level": 1, "max_grade_level": None,
                "hours_required": 3, "minutes_required": 4,
                "video_links": ['snakes.mp4', 'ladders.mp4'],
                'url': '/v1/quests/1', 'id': 1, 'name': 'mouse'},
            {'creator_id': 1, 'summary': 'blip', 'icon_url': None,
                'creator_url': '/v1/users/1', 'video_links': [],
                "inquiry_questions": [], 'tags': [],
                "pbl_description": None, "mentor_guide": None,
                "min_grade_level": None, "max_grade_level": None,
                "hours_required": None, "minutes_required": None,
                'url': '/v1/quests/2', 'id': 2, 'name': 'blouse'}])

        # delete
        resp = self.app.delete("/v1/quests/1")
        self.assertEqual(resp.status_code, 200)

        # and it's gone
        resp = self.app.get("/v1/quests/1")
        self.assertEqual(resp.status_code, 404)

        resp = self.put_json('/v1/quests/1', {
            'summary': 'nip', 'name': 'mouse',
            'icon_url': 'rubber'})
        self.assertEqual(resp.status_code, 404)

        resp = self.app.delete("/v1/quests/1")
        self.assertEqual(resp.status_code, 404)

    @harness.with_sess(user_id=1)
    def test_links(self):
        """Test linking quests and missions together."""

        # create the resources
        harness.create_user(name='snakes')

        resp = self.post_json(
                self.url_for(backend.quest_views.QuestList),
                {"name": "mouse", "summary": "nip"})
        self.assertEqual(resp.status_code, 200)

        resp = self.post_json(
                self.url_for(backend.quest_views.QuestList),
                {"name": "blouse", "summary": "blip"})
        self.assertEqual(resp.status_code, 200)

        resp = self.post_json(
                self.url_for(backend.mission_views.MissionList),
                {"name": "hat", "description": "snap", "points": 2})
        self.assertEqual(resp.status_code, 200)

        resp = self.post_json(
                self.url_for(backend.mission_views.MissionList),
                {"name": "cat", "description": "map", "points": 1})
        self.assertEqual(resp.status_code, 200)

        # no links yet
        resp = self.app.get(self.url_for(
            backend.quest_views.QuestMissionLinkList, mission_id=1))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.data)['quests'], [])

        resp = self.app.get(self.url_for(
            backend.quest_views.QuestMissionLinkList, mission_id=100))
        self.assertEqual(resp.status_code, 404)

        # create some links
        resp = self.app.put("/v1/missions/1/quests/1")
        self.assertEqual(resp.status_code, 200)

        resp = self.app.get(self.url_for(
            backend.quest_views.QuestMissionLinkList, mission_id=1))
        self.assertEqual(json.loads(resp.data)['quests'], [
            {"summary": "nip", "icon_url": None, "id": 1,
                "name": "mouse", "url": "/v1/quests/1", 'video_links': [],
                'inquiry_questions': [], 'tags': [],
                "pbl_description": None, "mentor_guide": None,
                "min_grade_level": None, "max_grade_level": None,
                "hours_required": None, "minutes_required": None,
                'creator_url': '/v1/users/1', "creator_id": 1}])

        resp = self.app.put("/v1/missions/1/quests/2")
        self.assertEqual(resp.status_code, 200)

        resp = self.app.get(self.url_for(
            backend.quest_views.QuestMissionLinkList, mission_id=1))
        self.assertItemsEqual(json.loads(resp.data)['quests'], [
            {"summary": "nip", "icon_url": None, "id": 1,
                "name": "mouse", "url": "/v1/quests/1", 'video_links': [],
                'inquiry_questions': [], 'tags': [],
                "pbl_description": None, "mentor_guide": None,
                "min_grade_level": None, "max_grade_level": None,
                "hours_required": None, "minutes_required": None,
                'creator_url': '/v1/users/1', "creator_id": 1},
            {'creator_id': 1, 'summary': 'blip',
                'creator_url': '/v1/users/1', 'video_links': [],
                'inquiry_questions': [], 'tags': [],
                "pbl_description": None, "mentor_guide": None,
                "min_grade_level": None, "max_grade_level": None,
                "hours_required": None, "minutes_required": None,
                'url': '/v1/quests/2', 'icon_url': None,
                'id': 2, 'name': 'blouse'}])

        # still nothing linked to this mission
        resp = self.app.get(self.url_for(
            backend.quest_views.QuestMissionLinkList, mission_id=2))
        self.assertEqual(json.loads(resp.data)['quests'], [])

        # check for idempotency
        resp = self.app.put("/v1/missions/1/quests/2")
        self.assertEqual(resp.status_code, 200)

        resp = self.app.get(self.url_for(
            backend.quest_views.QuestMissionLinkList, mission_id=1))
        self.assertItemsEqual(json.loads(resp.data)['quests'], [
            {"summary": "nip", "icon_url": None, "id": 1,
                "name": "mouse", "url": "/v1/quests/1", 'video_links': [],
                'inquiry_questions': [], 'tags': [],
                "pbl_description": None, "mentor_guide": None,
                "min_grade_level": None, "max_grade_level": None,
                "hours_required": None, "minutes_required": None,
                'creator_url': '/v1/users/1', "creator_id": 1},
            {'creator_id': 1, 'summary': 'blip',
                'creator_url': '/v1/users/1', 'video_links': [],
                'inquiry_questions': [], 'tags': [],
                "pbl_description": None, "mentor_guide": None,
                "min_grade_level": None, "max_grade_level": None,
                "hours_required": None, "minutes_required": None,
                'url': '/v1/quests/2', 'icon_url': None,
                'id': 2, 'name': 'blouse'}])

        # delete links
        resp = self.app.delete("/v1/missions/1/quests/2")
        self.assertEqual(resp.status_code, 200)

        resp = self.app.get(self.url_for(
            backend.quest_views.QuestMissionLinkList, mission_id=1))
        self.assertEqual(json.loads(resp.data)['quests'], [
            {"summary": "nip", "icon_url": None, "id": 1,
                "name": "mouse", "url": "/v1/quests/1", 'video_links': [],
                'inquiry_questions': [], 'tags': [],
                "pbl_description": None, "mentor_guide": None,
                "min_grade_level": None, "max_grade_level": None,
                "hours_required": None, "minutes_required": None,
                'creator_url': '/v1/users/1', "creator_id": 1}])

        resp = self.app.delete("/v1/missions/1/quests/1")
        self.assertEqual(resp.status_code, 200)

        resp = self.app.get(self.url_for(
            backend.quest_views.QuestMissionLinkList, mission_id=1))
        self.assertEqual(json.loads(resp.data)['quests'], [])

        # 404 on non-existent resources
        resp = self.app.delete("/v1/missions/1/quests/20")
        self.assertEqual(resp.status_code, 404)

        resp = self.app.delete("/v1/missions/30/quests/1")
        self.assertEqual(resp.status_code, 404)

    @harness.with_sess(user_id=1)
    def test_tags(self):
        """Test creation and linking of tags."""
        # nothing yet, so 404
        resp = self.app.get(self.url_for(backend.quest_views.Tag, tag_id=1))
        self.assertEqual(resp.status_code, 404)

        # create a user and some quests
        harness.create_user(name="snakes")

        resp = self.post_json(
                self.url_for(backend.quest_views.QuestList),
                {"name": "mouse", "summary": "hat"})
        self.assertEqual(resp.status_code, 200)

        resp = self.post_json(
                self.url_for(backend.quest_views.QuestList),
                {"name": "cat", "summary": "derby"})
        self.assertEqual(resp.status_code, 200)

        # create some resources
        resp = self.post_json(
                self.url_for(backend.quest_views.TagList), {"name": "a"})
        self.assertEqual(json.loads(resp.data), {
            "name": "a", "creator_id": 1, "creator_url": "/v1/users/1",
            "id": 1, "url": "/v1/quest-tags/1"})


        resp = self.post_json(
                self.url_for(backend.quest_views.TagList), {"name": "snakes"})
        self.assertEqual(json.loads(resp.data), {
            "name": "snakes", "creator_id": 1, "creator_url": "/v1/users/1",
            "id": 2, "url": "/v1/quest-tags/2"})

        # can't create two tags with the same name:
        resp = self.post_json(
                self.url_for(backend.quest_views.TagList), {"name": "a"})
        self.assertEqual(resp.status_code, 400)

        resp = self.put_json(
                self.url_for(backend.quest_views.Tag, tag_id=2), {"name": "a"})
        self.assertEqual(resp.status_code, 400)

        # edit
        resp = self.put_json(
                self.url_for(backend.quest_views.Tag, tag_id=2), {"name": "b"})
        self.assertEqual(resp.status_code, 200)

        resp = self.app.get(self.url_for(backend.quest_views.Tag, tag_id=2))
        self.assertEqual(json.loads(resp.data), {
            "name": "b", "creator_id": 1, "creator_url": "/v1/users/1",
            "id": 2, "url": "/v1/quest-tags/2"})

        # list them all
        resp = self.app.get(self.url_for(backend.quest_views.TagList))
        self.assertItemsEqual(json.loads(resp.data), {'tags': [
            {"creator_id": 1, "creator_url": "/v1/users/1",
                "id": 1, "name": "a", "url": "/v1/quest-tags/1"},
            {"creator_id": 1, "creator_url": "/v1/users/1",
                "id": 2, "name": "b", "url": "/v1/quest-tags/2"}]})

        # create some links
        resp = self.app.put(self.url_for(
            backend.quest_views.QuestTagLink, left_id=1, right_id=1))
        self.assertEqual(resp.status_code, 200)

        resp = self.app.put(self.url_for(
            backend.quest_views.QuestTagLink, left_id=1, right_id=2))
        self.assertEqual(resp.status_code, 200)

        resp = self.app.put(self.url_for(
            backend.quest_views.QuestTagLink, left_id=2, right_id=1))
        self.assertEqual(resp.status_code, 200)

        # idempotency check
        resp = self.app.put(self.url_for(
            backend.quest_views.QuestTagLink, left_id=1, right_id=1))
        self.assertEqual(resp.status_code, 200)

        # see the links
        resp = self.app.get(self.url_for(backend.quest_views.Quest, quest_id=1))
        self.assertItemsEqual(json.loads(resp.data)['tags'], [
            {'name': 'a', 'id': 1, 'url': '/v1/quest-tags/1'},
            {'name': 'b', 'id': 2, 'url': '/v1/quest-tags/2'}])

        resp = self.app.get(self.url_for(backend.quest_views.Quest, quest_id=2))
        self.assertItemsEqual(json.loads(resp.data)['tags'], [
            {'name': 'a', 'id': 1, 'url': '/v1/quest-tags/1'}])

        # remove a link
        resp = self.app.delete(self.url_for(
            backend.quest_views.QuestTagLink, left_id=1, right_id=1))
        self.assertEqual(resp.status_code, 200)

        resp = self.app.get(self.url_for(backend.quest_views.Quest, quest_id=1))
        self.assertItemsEqual(json.loads(resp.data)['tags'], [
            {'name': 'b', 'id': 2, 'url': '/v1/quest-tags/2'}])

        resp = self.app.get(self.url_for(backend.quest_views.Quest, quest_id=2))
        self.assertItemsEqual(json.loads(resp.data)['tags'], [
            {'name': 'a', 'id': 1, 'url': '/v1/quest-tags/1'}])

        # remove a resource
        resp = self.app.delete(self.url_for(backend.quest_views.Tag, tag_id=1))

        resp = self.app.get(self.url_for(backend.quest_views.Quest, quest_id=1))
        self.assertItemsEqual(json.loads(resp.data)['tags'], [
            {'name': 'b', 'id': 2, 'url': '/v1/quest-tags/2'}])

        resp = self.app.get(self.url_for(backend.quest_views.Quest, quest_id=2))
        self.assertItemsEqual(json.loads(resp.data)['tags'], [])

        resp = self.app.get(self.url_for(backend.quest_views.Tag, tag_id=1))
        self.assertEqual(resp.status_code, 404)

        resp = self.app.delete(self.url_for(backend.quest_views.Tag, tag_id=1))
        self.assertEqual(resp.status_code, 404)

        resp = self.put_json(
                self.url_for(backend.quest_views.Tag, tag_id=1), {'name': 'c'})
        self.assertEqual(resp.status_code, 404)


if __name__ == '__main__':
    unittest.main()
