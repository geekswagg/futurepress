__author__ = 'ajrenold'

# Lib Imports
from flask import ( request, session, g,
                    redirect, url_for, abort,
                    render_template, flash, jsonify,
                    make_response, Blueprint
                )
from werkzeug.contrib.atom import AtomFeed, FeedEntry
from flask.ext.stormpath import (
                                login_required,
                                user,
                                User
                            )

# Our Imports
from models import ( AppUser, Book, Genre, stormpathUserHash )


book_routes = Blueprint('book_routes', __name__,
                        template_folder='templates')

@book_routes.route('/books')
def books():
    title_search = request.args.get('title')
    genre = Genre.query.filter_by(name=request.args.get('genre')).first()
    books = Book.query.all()

    if title_search:
        books = Book.query.filter(Book.title.like('%'+title_search+'%')).all()
        return render_template('booklist.html', books=books, search_term=title_search, genre=None)

    if genre:
        books = [ b for b in books if genre in b.genres ]
        return render_template('booklist.html', books=books, search_term=None, genre=genre)

    #{{ url_for('book_routes.books', genre=genre.name) }}
    return render_template('booklist.html', books=books, search_term=None, genre=None)

@book_routes.route('/book/<int:book_id>')
def bookpage(book_id):
    if book_id:
        book = Book.query.get(book_id)
        if book:
            #return jsonify(book.as_dict())
            return render_template('bookpage.html', book=book)
    return redirect(url_for('index'))

@book_routes.route('/read/<int:book_id>')
def read(book_id):
    if book_id:
        book = Book.query.get(book_id)
        if book:
            return render_template('read.html', book=book)
    return redirect(url_for('index'))

@book_routes.route('/purchase/<int:book_id>', methods=['POST'])
@login_required
def purchase(book_id):
    user_href = user.get_id()
    app_user = AppUser.query.get(stormpathUserHash(user_href))

    book = Book.query.get(book_id)
    app_user.purchase_book(book)

    return redirect(url_for('user_routes.library'))

@book_routes.route('/book/<int:book_id>.atom')
def bookatom(book_id):
    book = Book.query.get(book_id)
    entry = FeedEntry(book.title,
             author=book.author.as_dict(),
             id=book.book_id,
             updated=book.last_updated,
             published=book.published,
             links=[
                 {'type': "image/jpeg",
                  'rel': "http://opds-spec.org/image",
                  'href': book.cover_large},
                 {'type': "image/jpeg",
                  'rel': "http://opds-spec.org/image/thumbnail",
                  'href': book.cover_large},
                 {'type': "application/epub+zip",
                  'rel': "http://opds-spec.org/acquisition",
                  'href': book.epub_url},
                 {'type': "application/atom+xml;type=entry;profile=opds-catalog",
                  'rel': "alternate",
                  'href': url_for('book_routes.bookpage', book_id=book.book_id, _external=True)},
             ]
    )
    response = make_response('<?xml version="1.0" encoding="UTF-8"?>\n'+
                             ''.join([ el for el in entry.generate() ]))
    response.headers['Content-Type'] = 'application/atom+xml'
    return response

@book_routes.route('/catalog.atom')
def catalog():
    feed = AtomFeed('FuturePress Catalog',
                    feed_url=request.url,
                    subtitle="FuturePress' full catalog")

    books = Book.query.all()
    for book in books:
        feed.add(book.title,
             author=book.author.as_dict(),
             id=book.book_id,
             updated=book.last_updated,
             published=book.published,
             links=[
                 {'type': "image/jpeg",
                  'rel': "http://opds-spec.org/image",
                  'href': book.cover_large},
                 {'type': "image/jpeg",
                  'rel': "http://opds-spec.org/image/thumbnail",
                  'href': book.cover_large},
                 {'type': "application/epub+zip",
                  'rel': "http://opds-spec.org/acquisition",
                  'href': book.epub_url},
                 {'type': "application/atom+xml;type=entry;profile=opds-catalog",
                  'rel': "alternate",
                  'href': url_for('book_routes.bookatom', book_id=book.book_id, _external=True)},
             ]
        )

    return feed.get_response()