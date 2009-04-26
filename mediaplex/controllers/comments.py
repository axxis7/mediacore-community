from tg import expose, validate, flash, require, url, request, redirect
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload

from mediaplex.model import DBSession, metadata, Video, Comment, Tag, Author
from mediaplex.model.comments import PUBLISH, PENDING_REVIEW, TRASH
from mediaplex.lib.base import BaseController

class CommentAdminController(BaseController):
    """Admin comment actions which deal with groups of comments"""

    @expose('mediaplex.templates.admin.comments.index')
    def index(self, search_string=None, **kwargs):
        return dict(page=self._fetch_page(search_string),
                    search_string=search_string,
                    published_status='publish',
                    awaiting_review_status='pending_review')

    @expose('mediaplex.templates.admin.comments.comment-table-ajax')
    def ajax(self, page_num, search_string=None):
        """ShowMore Ajax Fetch Action"""
        comments_page = self._fetch_page(search_string, page_num)
        return dict(page=comments_page,
                    search_string=search_string,
                    published_status='publish',
                    awaiting_review_status='pending_review')

    def _fetch_page(self, search_string=None, page_num=1, items_per_page=10):
        """Helper method for paginating comments results"""
        from webhelpers import paginate

        comments = DBSession.query(Comment)
        if search_string is not None:
            like_search = '%%%s%%' % (search_string,)
            comments = comments.filter(or_(Comment.subject.like(like_search),
                       Comment.body.like(like_search)))

        comments = comments.order_by(Comment.status.desc(), Comment.created_on)

        return paginate.Page(comments, page_num, items_per_page)

    @expose()
    def lookup(self, comment_id, *remainder, **kwargs):
        comment = CommentRowAdminController(comment_id)
        return comment, remainder

class CommentRowAdminController(object):
    """Admin comment actions which deal with a single comment"""

    def __init__(self, comment_id):
        """Pull the comment from the database for all actions"""
        self.comment = DBSession.query(Comment).filter_by(id=comment_id).one()

    @expose()
    def approve(self):
        self.comment.status = PUBLISH
        DBSession.add(self.comment)

    @expose()
    def trash(self):
        self.comment.status = TRASH
        DBSession.add(self.comment)
