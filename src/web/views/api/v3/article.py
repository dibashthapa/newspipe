from flask.ext.login import current_user
from web import models
from bootstrap import application, manager
from web.controllers import ArticleController
from web.views.api.v3.common import AbstractProcessor
from web.views.api.v3.common import url_prefix, auth_func

class ArticleProcessor(AbstractProcessor):
    def get_single_preprocessor(self, instance_id=None, **kw):
        # Check if the user is authorized to modify the specified
        # instance of the model.
        contr = ArticleController(current_user.id)
        article = contr.get(id=instance_id)
        if not self.is_authorized_to_modify(current_user, article):
            raise ProcessingException(description='Not Authorized', code=401)


article_processor = ArticleProcessor()

blueprint_article = manager.create_api_blueprint(models.Article,
        url_prefix=url_prefix,
        methods=['GET', 'POST', 'PUT', 'DELETE'],
        preprocessors=dict(GET_SINGLE=[auth_func,
                                    article_processor.get_single_preprocessor],
                           GET_MANY=[auth_func,
                                    article_processor.get_many_preprocessor],
                           PUT_SINGLE=[auth_func],
                           POST=[auth_func],
                           DELETE=[auth_func]))
application.register_blueprint(blueprint_article)