# -*- coding: utf-8 -*-
# If an error occurs, try:
# $ ./manage.py shell
# ...
# >>> execfile('init_db.py')
# for better debug message

from random import randint
import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from newspaper import ArticleException

from core.exceptions import ServiceUnavailable
from common.models import Category, Keyword
from common import enums
from users.models import UserRole
from orgs.models import Organization, OrganizationUser
from tasks.models import TaskBrief, Task
from jobs.models import Job, Application
from articles.serializers import ImportedArticleCreateSerializer

User = get_user_model()


def set_user_profile_picture(user, picture_url):
    user_profile = user.userprofile
    user_profile.picture = 'user_images/' + picture_url
    user_profile.save()


def set_user_profile_description(user, description):
    user_profile = user.userprofile
    user_profile.description = description
    user_profile.save()


def set_task_completed_time(task, completed_time):
    # Task.objects.filter(id=task.id).update(modified=completed_time)
    for field in task._meta.local_fields:
        if field == 'modified':
            field.auto_now_add = False
    task.modified = completed_time


def import_user_article(user, article_url):
    print 'importing user %s\'s article %s...' % (user, article_url),
    article_serializer = ImportedArticleCreateSerializer(
        data={'url': article_url}, user=user
    )
    try:
        article_serializer.is_valid(raise_exception=True)
        article_serializer.save(user=user)
        print 'OK'
    except ValidationError as exc:
        print ('ERROR: %s' % exc.detail)
    except (ArticleException, ServiceUnavailable) as exc:
        print ('ERROR: %s' % exc)


def import_user_articles(user, article_urls):
    for url in article_urls:
        import_user_article(user, url)


class CategoryEnum(object):
    ART_DESIGN = 1
    BUSINESS = 2
    EDUCATION = 3
    ENTERTAINMENT = 4
    FOOD_BEVERAGE = 5
    HEALTHCARE_SCIENCES = 6
    LIFESTYLE_TRAVEL = 7
    PUBLISHING_JOURNALISM = 8
    SOFTWARE_TECHNOLOGY = 9
    SPORT_FITNESS = 10


User.objects.create_superuser(
    username='admin',
    email='hi@connverse.me',
    password='password'
)

savy = User.objects.create_user(
    username='savy',
    first_name='Savdeep Singh',
    last_name='Gandhi',
    email='savdeep@connverse.me',
    password='password'
)
UserRole.objects.create(user=savy, role=enums.UserRole.BUSINESS)
set_user_profile_picture(savy, 'ken.jpg')

pan = User.objects.create_user(
    username='pan',
    first_name='Pan',
    last_name='An',
    email='pan@connverse.me',
    password='password'
)
UserRole.objects.create(user=pan, role=enums.UserRole.BUSINESS)
set_user_profile_picture(pan, 'tim.jpeg')

lavanya = User.objects.create_user(
    username='lavanya',
    first_name='Lavanya',
    last_name='Arunachalam',
    email='lavanaya@connverse.me',
    password='password'
)
UserRole.objects.create(user=lavanya, role=enums.UserRole.BUSINESS)
set_user_profile_picture(lavanya, 'yiwen.jpeg')


connverse_media = Organization.objects.create(
    name='Connverse Pte Ltd',
    website='connverse.me',
    description='Connect brands to the right voice',
    industry='Media',
    year_founded=2015,
    size=6
)
OrganizationUser.objects.create(
    user=savy,
    organization=connverse_media,
    user_role=OrganizationUser.USER_ROLE_EMPLOYEE
    # fuck you savy, I don't want to see your name every time I debug.
)

# pan & lavanya are in-house writer/editor
OrganizationUser.objects.create(
    user=pan,
    organization=connverse_media,
    user_role=OrganizationUser.USER_ROLE_OWNER
)
OrganizationUser.objects.create(
    user=lavanya,
    organization=connverse_media,
    user_role=OrganizationUser.USER_ROLE_EMPLOYEE
)
# Creation of new organisation DBS
raj = User.objects.create_user(
    username='raj',
    first_name='Rajender',
    last_name='Kumar',
    email='raj@dbs.com',
    password='password'
)
UserRole.objects.create(user=raj, role=enums.UserRole.BUSINESS)

dbs = Organization.objects.create(
    name='DBS Singapore',
    website='www.dbs.com',
    description='DBS Bank Ltd is a Singaporean multinational banking and financial services company. The company was known as The Development Bank of Singapore Limited, before the present name was adopted in July 2003 to reflect its changing role as a regional bank',
    industry='Banking',
    year_founded=1989,
    size=10000
)
OrganizationUser.objects.create(
    user=raj,
    organization=dbs,
    user_role=OrganizationUser.USER_ROLE_OWNER
)

# Creation of Sph
howard = User.objects.create_user(
    username='howard',
    first_name='Howard',
    last_name='Rouson',
    email='howard@sph.com',
    password='password'
)
UserRole.objects.create(user=howard, role=enums.UserRole.BUSINESS)

sph = Organization.objects.create(
    name='SPH Singapore',
    website='www.sph.com',
    description='Singapore Press Holdings Limited is a media organisation in Singapore with businesses in print, Internet and new media, television and radio, outdoor media, and property. SPH has over 5,000 employees, including a team of approximately 1,000 journalists, including correspondents operating around the world. The company is one of the country "blue-chip" counters on the Singapore Stock Exchange, and makes about S$480–500 million worth of profits every year.',
    industry='Media',
    year_founded=1976,
    size=5007
)
OrganizationUser.objects.create(
    user=howard,
    organization=sph,
    user_role=OrganizationUser.USER_ROLE_OWNER
)

# sample freelancers
justin_harper = User.objects.create_user(
    username='justinharper',
    first_name='Justin',
    last_name='Harper',
    email='justinharper@boltmedia.co',
    password='password'
)
set_user_profile_description(justin_harper, 'Money, finance, international business news. Ex-telegraph journalist.')
set_user_profile_picture(justin_harper, 'justin_harper.jpg')
UserRole.objects.create(user=justin_harper, role=enums.UserRole.WRITER)
import_user_articles(justin_harper, [
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/11282921/Top-buy-to-let-hot-spots-in-Britain.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/11171374/New-way-to-keep-up-with-French-property-prices.html',
    'http://www.telegraph.co.uk/expat/expatnews/11149093/Singapore-has-a-new-sports-hub.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/11115167/New-freeport-where-all-prized-assets-bar-human-hair-can-be-stashed.html',
    'http://www.telegraph.co.uk/education/expateducation/10980891/A-Newcastle-University-education-in-a-much-warmer-location.html',
    'http://www.telegraph.co.uk/expat/expatnews/10909266/Expats-battling-incinerator-in-Hong-Kong.html',
    'http://www.telegraph.co.uk/expat/expatnews/10887252/Passport-delays-prompting-drastic-measures.html',
    'http://www.telegraph.co.uk/expat/expatnews/10870409/Passport-renewal-delays-causing-expat-headaches.html',
    'http://www.telegraph.co.uk/education/expateducation/10826930/British-school-to-open-in-Burma.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/10784827/Discounted-Aston-Martins-for-Singapore-apartment-buyers.html',
    'http://www.telegraph.co.uk/expat/before-you-go/10785600/Expat-guide-renting-out-your-UK-home.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/10779428/London-and-New-York-are-the-top-world-cities.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/10754544/How-to-cut-US-tax-bills-by-helping-typhoon-victims.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/10740210/Tesco-to-invest-in-India.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/10727217/Airlines-and-travellers-unimpressed-by-passenger-duty-cut.html',
    'http://www.telegraph.co.uk/education/expateducation/10720923/Local-students-dominating-British-international-schools.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/10719777/Expat-tax-break-threatened-spelling-bad-news-for-pensioners.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/10708606/Nows-a-tempting-time-to-invest-in-property-Down-Under.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/10704863/Trendy-Asian-shoppers-embracing-traditional-British-menswear.html',
    'http://www.telegraph.co.uk/expat/expatnews/10681387/Former-POWs-revisit-Singapore-as-new-memorial-is-unveiled.html',
    'http://www.telegraph.co.uk/expat/expatnews/10658816/British-rugby-star-tackles-a-new-challenge-at-sea.html',
    'http://www.telegraph.co.uk/expat/expatnews/10615354/Japan-plans-to-lure-more-expats.html',
    'http://www.telegraph.co.uk/education/expateducation/10590290/British-students-urged-to-taste-life-in-China.html',
    'http://www.telegraph.co.uk/finance/property/expat-property/10584813/Expats-granted-increased-property-rights-in-Abu-Dhabi.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/10568277/Note-trips-home-to-avoid-a-tax-shock.html',
    'http://www.telegraph.co.uk/telegraph/expat/contributors/justinharper/?showPageNumber=2',
    'http://www.telegraph.co.uk/expat/expatlife/10557283/Its-time-to-turn-out-the-lights-again.html',
    'http://www.telegraph.co.uk/expat/10537270/Canada-plans-to-lure-more-expats-in-2014.html',
    'http://www.telegraph.co.uk/expat/expatlife/10530042/Virtual-Private-Networks-can-help-expats-missing-British-TV.html',
    'http://www.telegraph.co.uk/expat/expatnews/10505324/Expat-food-orders-heavy-on-sugar-and-spice-and-all-things-nice.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/10495879/A-short-term-gig-or-a-forever-home-The-stats-that-tell-the-story.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/10488298/Singapores-high-Rollers-love-their-customised-cars.html',
    'http://www.telegraph.co.uk/expat/expatnews/10473427/Top-three-cities-pulling-in-expats-are-all-in-Australia.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/10453326/To-beat-inflation-pick-China-over-South-America.html',
    'http://www.telegraph.co.uk/expat/expatlife/10446889/Flying-to-Singapore-then-and-now.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/10440636/Expat-pensioners-in-Canada-hit-hardest-by-weakened-pound.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/10430200/UK-links-with-Turkey-boosted-by-cross-continental-tunnel.html',
    'http://www.telegraph.co.uk/finance/personalfinance/expat-money/10426031/Investing-in-student-property-overseas-can-put-you-streets-ahead.html'
])


grace_ma = User.objects.create_user(
    username='grace_ma',
    first_name='Grace',
    last_name='Ma',
    email='gracema@boltmedia.co',
    password='password'
)
set_user_profile_description(grace_ma, 'Writer & Journalist for SMU, SPH and The Edge.')
set_user_profile_picture(grace_ma, 'grace_ma.jpg')
UserRole.objects.create(user=grace_ma, role=enums.UserRole.WRITER)
import_user_articles(grace_ma, [
    'http://sphclass.com.sg/scholarschoice/articles/smu1.html',
    'http://sphclass.com.sg/scholarschoice/articles/pub1.html',
    'http://travel.asiaone.com/article/destinations/turkish-feast-for-the-senses',
    'http://travel.asiaone.com/article/interests/luxe-in-the-cruise',
    'http://travel.asiaone.com//article/features/beauty-and-the-reef',
    'http://sphclass.com.sg/scholarschoice/articles/nea1.html',
])

katie_sargent = User.objects.create_user(
    username='katie_sargent',
    first_name='Katie',
    last_name='Sargent',
    email='katiesargent@boltmedia.co',
    password='password'
)
set_user_profile_description(katie_sargent, 'Ex-Reuters & CNBC Producer. Posts about small business and markets.')
set_user_profile_picture(katie_sargent, 'katie_sargent.jpg')
UserRole.objects.create(user=katie_sargent, role=enums.UserRole.WRITER)
import_user_articles(katie_sargent, [
    'http://thinkbusiness.nus.edu/articles/item/203-government-in-business-no-apologies-necessary',
    'http://thinkbusiness.nus.edu/articles/item/226-chindia-jagdish-sheth',
    'http://thinkbusiness.nus.edu/articles/item/274-when-pigs-fly-baidu-founder-on-building-the-next-big-thing',
    'http://thinkbusiness.nus.edu/articles/item/266-creating-climate-wealth-the-gigaton-effect',
    'http://mypaper.sg/opinion/celebrity-marketing-pays-osim-20131218',
])

lilian_koh = User.objects.create_user(
    username='lilian',
    first_name='Lilian',
    last_name='Koh',
    email='liliankoh@boltmedia.co',
    password='password'
)
set_user_profile_description(lilian_koh, 'Detail-oriented, ex-Jakarta Post journalst. Interested in latest consumer gadgets!')
set_user_profile_picture(lilian_koh, 'lilian_koh.png')
UserRole.objects.create(user=lilian_koh, role=enums.UserRole.WRITER)
import_user_articles(lilian_koh, [
    'http://techcrunch.com/2015/10/19/nexus-6p-review-this-is-the-android-device-that-youve-been-waiting-for/',
    'http://techcrunch.com/2015/10/19/nexus-5x-review-googles-second-best-flagship-device/',
    'http://techcrunch.com/2015/10/18/denim-denim-denim/',
    'http://techcrunch.com/2015/10/18/the-social-web-and-the-digital-panopticon/',
    'http://techcrunch.com/2015/10/19/meet-me-in-st-louis-for-the-first-tc-meet-up-and-pitch-off/',
    'http://techcrunch.com/2015/10/19/flipboard-launches-a-new-targeted-ads-product-based-on-interests/',
    'http://techcrunch.com/2015/10/19/facebook-now-warns-users-if-theyre-a-target-of-state-sponsored-attacks/',
    'http://techcrunch.com/2015/10/19/time-inc-acquires-hello-giggles/',
    'http://www.straitstimes.com/singapore/education/169-childcare-centres-run-by-23-partner-operators-to-cut-fees-from-2016',
    'http://www.straitstimes.com/singapore/transport/more-space-at-17-mrt-station-platforms-by-2018',
    'http://www.straitstimes.com/business/economy/pm-lee-hsien-loong-opens-fusionopolis-two-rd-has-benefitted-singaporeans-and-the',
    'http://www.straitstimes.com/singapore/environment/singapore-team-in-palembang-carries-out-47-water-bombing-operations-puts-out',
    'http://www.straitstimes.com/singapore/secret-police-bunker-in-chinatown-opens-to-public',
    'http://www.straitstimes.com/business/economy/china-gdp-growth-falls-to-69-in-q3-just-above-expectations',
    'http://www.straitstimes.com/asia/se-asia/malaysia-opposition-chief-wan-azizah-to-table-no-confidence-motion-against-pm-najib',
    'http://www.straitstimes.com/world/europe/britain-unveils-new-counter-extremism-measures',
    'http://www.straitstimes.com/world/middle-east/new-saudi-performance-centre-adds-to-top-princes-powers',
    'http://www.straitstimes.com/singapore/into-the-future',
    'http://www.straitstimes.com/tech/start-ups-buccaneer-3d-printer-venture-sinks',
    'http://www.straitstimes.com/tech/firms-fight-over-mobile-band',
    'http://www.straitstimes.com/tech/battle-for-eyeballs-how-tv-companies-are-wooing-consumers-with-their-smart-tv-platforms',
    'http://www.straitstimes.com/tech/games-apps/fifa-16-as-gorgeous-as-before-but-trickier-to-win',
    'http://www.straitstimes.com/tech/apple-ordered-to-pay-us234-million-to-university-for-infringing-patent',
    'http://www.straitstimes.com/tech/food-junction-rolls-out-nets-cashless-payments',
    'http://e27.co/journey-smart-nation-important-aaron-maniam-20151019/',
    'http://e27.co/daum-co-founder-taekkyung-lee-on-his-love-for-startups-part-2-20151019/',
    'http://e27.co/top-4-meowsome-gadgets-20151019/',
    'http://e27.co/infographic-hong-kong-new-tech-hub-east-20151019/',
    'http://e27.co/chope-thailands-gm-speak-founders-drinks-bangkok-20151019/',
    'http://e27.co/global-expansion-sight-indias-dineout-thanks-inresto-acquisition-20151019/',
    'https://vulcanpost.com/414151/witching-hours-game-developer-gaming-in-singapore/',
    'https://vulcanpost.com/406441/aegis-pro-earphones-blast-music-while-staying-safe/',
    'https://vulcanpost.com/414471/kayak-new-feature-make-travelling-seem-cheaper/',
    'http://www.todayonline.com/singapore/23-childcare-operators-get-funding-keep-fees-affordable-raise-quality',
    'http://www.todayonline.com/singapore/taxi-falls-stairway',
    'http://www.todayonline.com/world/french-jet-dangerous-incident-russian-aircraft-moscow',
    'http://www.todayonline.com/business/valeant-pharma-revenue-rises-36-percent'
    'http://www.reuters.com/article/2015/10/19/us-wal-mart-suppliers-insight-idUSKCN0SD0CZ20151019',
])

vincent = User.objects.create_user(
    username='vincent',
    first_name='Vincent',
    last_name='Ng',
    email='vincent@boltmedia.co',
    password='password'
)
UserRole.objects.create(user=vincent, role=enums.UserRole.WRITER)

roy = User.objects.create_user(
    username='roy',
    first_name='Roy',
    last_name='New',
    email='roy@boltmedia.co',
    password='password'
)
UserRole.objects.create(user=roy, role=enums.UserRole.WRITER)

emily = User.objects.create_user(
    username='emily',
    first_name='Emily',
    last_name='Chan',
    email='emily@boltmedia.co',
    password='password'
)
UserRole.objects.create(user=emily, role=enums.UserRole.WRITER)


task_brief = TaskBrief.objects.create(
    creator=savy,
    organization=connverse_media,
    title="Demo Day Press Coverage",
    description="Bring Him Home!!",
    deadline=datetime.date(2016, 01, 17)
)

task_brief.set_categories([
    Category.objects.get(pk=CategoryEnum.ENTERTAINMENT)
])
task_brief.set_keywords([
    Keyword.objects.get_or_create(name=keyword)[0]
    for keyword in ['martian', 'movie', 'hollywood']
])

# writing task
writing_task = Task.objects.create(
    task_brief=task_brief, type=enums.TaskType.WRITING,
    deadline=datetime.date(2016, 01, 15),
    description="Watch the Martian!!!"
)

writing_task_meta = writing_task.writing_meta
writing_task_meta.word_count = 100
writing_task_meta.content_type = enums.WritingContentType.PRESS_RELEASE
writing_task_meta.goal = enums.WritingGoal.PROMOTE_TOPIC
writing_task_meta.style = enums.WritingStyle.VIRAL
writing_task_meta.point_of_view = enums.WritingPointOfView.FIRST_PERSON
writing_task_meta.save()

# in-house writer
writing_task.set_assignee(lavanya, savy)

# config task ordering: writing -> accept
accept_task = task_brief.accept_task()
writing_task.set_successor(accept_task)

# publish task brief
task_brief.published = True
task_brief.save()

# yiwen wrote the article
article = task_brief.article
article.save_revision(
    author=lavanya,
    title='Interstellar with quips',
    content="""
    <div gravityNodes="13" gravityScore="463"><p>
If it&#8217;s the goal of great science
fiction to boldly go where no man has gone before, an entry-level
problem for The Martian is that it seems to be planting its space
boots in some very recently trodden turf.</p>
<p>For Matt Damon, the whole movie is another lost in space pick-up
attempt, after his similar part in Interstellar. For Ridley Scott it&#8217;s
another disaster-strewn voyage into the cosmos, after his own return
to the genre with<a href="http://www.telegraph.co.uk/film/prometheus-2/plot-cast-rumours-spoilers/"><b>Prometheus</b></a>.
Is this a new frontier to explore, or just a disco remix?</p>
<p>The difference from both of those movies is ambition (lower) and
tone (much, much lighter). Adapting the self-published<b> <a href="http://www.telegraph.co.uk/film/the-martian/andy-weir-author-interview/" target="_blank">novel by Andy Weir</a></b>, Scott and his
screenwriter, Lost and Cabin in the Woods scribe Drew Goddard, get the
premise speedily up and running: a manned mission to Mars, with six
astronauts tasked with bringing back samples, is thrown into disarray
when heavy weather blows in.</p>
<p>One of their number, botanist Mark Watney (Damon), is hit by flying
debris and thrown out of sight; his communications and life signs both
go dead; and the other five, played by Jessica Chastain, Kate Mara,
Sebastian Stan, Aksel Hennie and Michael Pe&#241;a, have no choice but to
abort their mission and head back to Earth.</p>
<p>&#8220;I&#8217;m not dead,&#8221; the injured Mark reports on regaining
consciousness, in a first recorded missive which he has no means to
convey to Nasa. &#8220;Obviously.&#8221; That&#8217;s a very Goddard &#8220;obviously&#8221; &#8211; you
hear his smart, wisecracking voice constantly scanning the joint for
comic potential.</p>
</div>
    """
)

# complete brief
writing_task.status = enums.TaskStatus.FINISHED
set_task_completed_time(writing_task, datetime.date(2016, 01, 12))
writing_task.save()
accept_task.status = enums.TaskStatus.FINISHED
set_task_completed_time(accept_task, datetime.date(2016, 01, 15))
accept_task.save()


# task brief with 1 writing task & 1 editing task
task_brief = TaskBrief.objects.create(
    creator=savy,
    organization=connverse_media,
    title="User Study Reports",
    description="Exact project brief will be provided to shortlisted freelancers.",
    deadline=datetime.date(2016, 03, 30)
)

task_brief.set_categories([
    Category.objects.get(pk=CategoryEnum.EDUCATION)
])
task_brief.set_keywords([
    Keyword.objects.get_or_create(name=keyword)[0]
    for keyword in ['academic', 'case study']
])

# writing task
writing_task = Task.objects.create(
    task_brief=task_brief, type=enums.TaskType.WRITING,
    deadline=datetime.date(2016, 02, 15)
)

writing_task_meta = writing_task.writing_meta
writing_task_meta.word_count = 100
writing_task_meta.content_type = enums.WritingContentType.SHORT_BLOG_POST
writing_task_meta.goal = enums.WritingGoal.EDUCATE_INSTRUCT
writing_task_meta.style = enums.WritingStyle.AUTHORATIATIVE
writing_task_meta.point_of_view = enums.WritingPointOfView.THIRD_PERSON
writing_task_meta.save()


# post to market place
job = Job.objects.create(
    task=writing_task, price=100,
    closing_date=datetime.date(2016, 02, 8),
    description="Require an a freelancer for an urgent project which requires"
    " knowledge of discounted cash flows, construction, development finance"
    " and risk analysis. Please do not send your interest if you are not"
    " able to demonstrate knowledge in these areas. Must be completed within"
    " 48 hours. "
)


# editing task
editing_task = Task.objects.create(
    task_brief=task_brief, type=enums.TaskType.EDITING,
    deadline=datetime.date(2016, 02, 25),
    description="Alter style to be consistent with our existing articles"
)

# assign to in-house member
editing_task.set_assignee(pan, savy)

# config task ordering: writing -> editing -> accept
accept_task = task_brief.accept_task()
editing_task.set_successor(accept_task)
writing_task.set_successor(editing_task)

# publish the brief
task_brief.published = True
task_brief.save()


# mock applications
grace_ma_application = Application.objects.create(
    job=job, applicant=grace_ma,
    message="I did my MBA at Stanford!",
)
emily_application = Application.objects.create(
    job=job, applicant=emily,
    message="I have 100k followers on Facebook.",
)
roy_application = Application.objects.create(
    job=job, applicant=roy,
    message="I have 100k followers on Facebook.",
)

# grace_ma is accepted, others are rejected
grace_ma_application.status = enums.ApplicationStatus.ACCEPTED
grace_ma_application.save()


# task brief with 1 writing task (external) & 1 editing task (inhouse)
task_brief = TaskBrief.objects.create(
    creator=savy,
    organization=connverse_media,
    title="Connverse Press Release",
    description="Great story to be featured on TechCrunch!",
    deadline=datetime.date(2016, 03, 30)
)

task_brief.set_categories([
    Category.objects.get(pk=CategoryEnum.PUBLISHING_JOURNALISM)
])
task_brief.set_keywords([
    Keyword.objects.get_or_create(name=keyword)[0]
    for keyword in ['techcrunch', 'press release', 'Connverse',
                    'content marketing']
])

# writing task
writing_task = Task.objects.create(
    task_brief=task_brief, type=enums.TaskType.WRITING,
    deadline=datetime.date(2016, 02, 24)
)

writing_task_meta = writing_task.writing_meta
writing_task_meta.word_count = 100
writing_task_meta.content_type = enums.WritingContentType.SHORT_BLOG_POST
writing_task_meta.goal = enums.WritingGoal.PROVIDE_INFORMED_ANALYSIS
writing_task_meta.style = enums.WritingStyle.AUTHORATIATIVE
writing_task_meta.point_of_view = enums.WritingPointOfView.THIRD_PERSON
writing_task_meta.save()


# post to market place
job = Job.objects.create(
    task=writing_task, price=100,
    closing_date=datetime.date(2016, 02, 24),
    description="Experienced freelancer required. Published articles on"
    "TechCrunch is a plus"
)


# editing task
editing_task = Task.objects.create(
    task_brief=task_brief, type=enums.TaskType.EDITING,
    deadline=datetime.date(2016, 02, 28),
    description=""
)

# assign to in-house member
editing_task.set_assignee(pan, savy)

# config task ordering: writing -> editing -> accept
accept_task = task_brief.accept_task()
editing_task.set_successor(accept_task)
writing_task.set_successor(editing_task)

# publish the brief
task_brief.published = True
task_brief.save()


# mock applications
katie_sargent_application = Application.objects.create(
    job=job, applicant=katie_sargent,
    message="I did my MBA at Stanford!",
)
roy_application = Application.objects.create(
    job=job, applicant=emily,
    message="I have 100k followers on Facebook.",
)

# yiwen is accepted, others are rejected
katie_sargent_application.status = enums.ApplicationStatus.ACCEPTED
katie_sargent_application.save()


# task brief with 1 writing task (external), submited for review
task_brief = TaskBrief.objects.create(
    creator=savy,
    organization=connverse_media,
    title="Natural Language Processing Academic Paper",
    description="I am providing you with the literature to review and I want"
    " it critically examined in relation to consumer behaviour.",
    deadline=datetime.date(2015, 10, 22)
)
task_brief.set_categories([
    Category.objects.get(pk=CategoryEnum.EDUCATION)
])
task_brief.set_keywords([
    Keyword.objects.get_or_create(name=keyword)[0]
    for keyword in ['education', 'academic']
])

# writing task
writing_task = Task.objects.create(
    task_brief=task_brief, type=enums.TaskType.WRITING,
    deadline=datetime.date(2015, 10, 17)
)

writing_task_meta = writing_task.writing_meta
writing_task_meta.word_count = 100
writing_task_meta.content_type = enums.WritingContentType.ARTICLE
writing_task_meta.goal = enums.WritingGoal.EDUCATE_INSTRUCT
writing_task_meta.style = enums.WritingStyle.INSTRUCTIONAL
writing_task_meta.point_of_view = enums.WritingPointOfView.FIRST_PERSON
writing_task_meta.save()


# post to market place
job = Job.objects.create(
    task=writing_task, price=100,
    closing_date=datetime.date(2015, 10, 10),
    description="""
    Headings for the research paper:
    - Introduction to the Industry
    - Specific Area of Interest Literature (EG. Social Media in the Automotive Industry, Recruitment 4.0, Tourism Techniques in the Digital Landscape)
    - Key Themes in Literature
    - Research Proposal the attitude of soccer fans in relation to sales promotion on social media (twitter)
    - Proposed research question do fans reach positively or negatively to sales promotion on social media (twitter)
    - Research Objectives to determine if fans would react positively to sales promotion or want to protect the feeds of sales promotion as this is the only platform where they can interact with the brand.
    - Research Methodology mainly quantitative
    - Key Sources: once the project is awarded I will provide the literature I want reviewe
    """
)

# config task ordering: writing -> accept
accept_task = task_brief.accept_task()
writing_task.set_successor(accept_task)


# publish the brief
task_brief.published = True
task_brief.save()


# mock applications
katie_sargent_application = Application.objects.create(
    job=job, applicant=katie_sargent,
    message="I have 10 years of writing experience. Hire me!",
)
justin_harper_application = Application.objects.create(
    job=job, applicant=justin_harper,
    message="I have 100k followers on Facebook.",
)
grace_ma_application = Application.objects.create(
    job=job, applicant=grace_ma,
    message="I did my MBA at Stanford!",
)

# roy is accepted, others are rejected
justin_harper_application.status = enums.ApplicationStatus.ACCEPTED
justin_harper_application.save()


# roy started writing some content on the article
article = task_brief.article
article.save_revision(
    author=justin_harper,
    title='Shakespeare\'s plays',
    content="""
<div gravityNodes="35" gravityScore="1771"><p><b>William Shakespeare's plays</b> have the reputation of being among the greatest in the English language and in <a href="/wiki/Western_literature" title="Western literature">Western literature</a>. Traditionally, the plays are divided into the genres of <a href="/wiki/Shakespearean_tragedy" title="Shakespearean tragedy">tragedy</a>, <a href="/wiki/Shakespearean_history" title="Shakespearean history">history</a>, and <a href="/wiki/Shakespearean_comedy" title="Shakespearean comedy">comedy</a>; they have been translated into every major <a href="/wiki/Modern_language" title="Modern language">living</a> <a href="/wiki/Language" title="Language">language</a>, in addition to being continually performed all around the world.</p>
<p>Many of his plays appeared in print as a series of <a class="mw-redirect" href="/wiki/Folios_and_Quartos_(Shakespeare)" title="Folios and Quartos (Shakespeare)">quartos</a>, but approximately half of them remained unpublished until 1623, when the posthumous <a href="/wiki/First_Folio" title="First Folio">First Folio</a> was published. The traditional division of his plays into tragedies, comedies and histories follows the categories used in the First Folio. However, modern criticism has labelled some of these plays "<a href="/wiki/Shakespearean_problem_play" title="Shakespearean problem play">problem plays</a>" that elude easy categorisation, or perhaps purposely break generic conventions, and has introduced the term <a href="/wiki/Shakespeare%27s_late_romances" title="Shakespeare's late romances">romances</a> for what scholars believe to be his later comedies.</p>
<p>When <a href="/wiki/William_Shakespeare" title="William Shakespeare">Shakespeare</a> first arrived in London in the late 1580s or early 1590s, dramatists writing for London's new commercial playhouses (such as <a href="/wiki/Curtain_Theatre" title="Curtain Theatre">The Curtain</a>) were combining two different strands of dramatic tradition into a new and distinctively Elizabethan synthesis. Previously, the most common forms of popular English theatre were the <a href="/wiki/Tudor_period" title="Tudor period">Tudor</a> <a href="/wiki/Morality_play" title="Morality play">morality plays</a>. These plays, celebrating <a href="/wiki/Piety" title="Piety">piety</a> generally, use <a class="mw-redirect" href="/wiki/Personification" title="Personification">personified</a> moral attributes to urge or instruct the <a href="/wiki/Protagonist" title="Protagonist">protagonist</a> to choose the virtuous life over Evil. The characters and plot situations are largely symbolic rather than realistic. As a child, Shakespeare would likely have seen this type of play (along with, perhaps, <a href="/wiki/Mystery_play" title="Mystery play">mystery plays</a> and <a class="mw-redirect" href="/wiki/Miracle_play" title="Miracle play">miracle plays</a>).<sup class="reference" id="cite_ref-1"><a href="#cite_note-1">[1]</a></sup></p>
<p>The other strand of dramatic tradition was <a href="/wiki/Classical_antiquity" title="Classical antiquity">classical</a> aesthetic theory. This theory was derived ultimately from <a href="/wiki/Aristotle" title="Aristotle">Aristotle</a>; in Renaissance England, however, the theory was better known through its Roman interpreters and practitioners. At the universities, plays were staged in a more academic form as <a href="/wiki/Roman_Empire" title="Roman Empire">Roman</a> closet dramas. These plays, usually performed in <a class="mw-redirect" href="/wiki/Latin_language" title="Latin language">Latin</a>, adhered to classical ideas of <a href="/wiki/Classical_unities" title="Classical unities">unity</a> and <a href="/wiki/Decorum" title="Decorum">decorum</a>, but they were also more static, valuing lengthy speeches over physical action. Shakespeare would have learned this theory at grammar school, where <a href="/wiki/Plautus" title="Plautus">Plautus</a> and especially <a href="/wiki/Terence" title="Terence">Terence</a> were key parts of the curriculum<sup class="reference" id="cite_ref-2"><a href="#cite_note-2">[2]</a></sup> and were taught in editions with lengthy theoretical introductions.<sup class="reference" id="cite_ref-3"><a href="#cite_note-3">[3]</a></sup></p>
<p />
<p />

<p>Archaeological excavations on the foundations of the <a href="/wiki/The_Rose_(theatre)" title="The Rose (theatre)">Rose</a> and the <a href="/wiki/Globe_Theatre" title="Globe Theatre">Globe</a> in the late twentieth century<sup class="reference" id="cite_ref-4"><a href="#cite_note-4">[4]</a></sup> showed that all London <a href="/wiki/English_Renaissance_theatre" title="English Renaissance theatre">English Renaissance theatres</a> were built around similar general plans. Despite individual differences, the public theatres were three stories high, and built around an open space at the centre. Usually polygonal in plan to give an overall rounded effect, three levels of inward-facing galleries overlooked the open centre into which jutted the stage&#8212;essentially a platform surrounded on three sides by the audience, only the rear being restricted for the entrances and exits of the actors and seating for the musicians. The upper level behind the stage could be used as a <a href="/wiki/Balcony" title="Balcony">balcony</a>, as in <i><a href="/wiki/Romeo_and_Juliet" title="Romeo and Juliet">Romeo and Juliet</a></i>, or as a position for a character to harangue a crowd, as in <i><a href="/wiki/Julius_Caesar_(play)" title="Julius Caesar (play)">Julius Caesar</a></i>.</p>
<p>Usually built of timber, lath and plaster and with thatched roofs, the early theatres were vulnerable to fire, and gradually were replaced (when necessary) with stronger structures. When the Globe burned down in June 1613, it was rebuilt with a tile roof.</p>
<p>A different model was developed with the <a href="/wiki/Blackfriars_Theatre" title="Blackfriars Theatre">Blackfriars Theatre</a>, which came into regular use on a long term basis in 1599. The Blackfriars was small in comparison to the earlier theatres, and roofed rather than open to the sky; it resembled a modern theatre in ways that its predecessors did not.</p>

<p>For Shakespeare as he began to write, both traditions were alive; they were, moreover, filtered through the recent success of the <a href="/wiki/University_Wits" title="University Wits">University Wits</a> on the London stage. By the late 16th century, the popularity of morality and academic plays waned as the <a href="/wiki/English_Renaissance" title="English Renaissance">English Renaissance</a> took hold, and playwrights like <a href="/wiki/Thomas_Kyd" title="Thomas Kyd">Thomas Kyd</a> and <a href="/wiki/Christopher_Marlowe" title="Christopher Marlowe">Christopher Marlowe</a> revolutionised theatre. Their plays blended the old morality drama with classical theory to produce a new secular form.<sup class="reference" id="cite_ref-5"><a href="#cite_note-5">[5]</a></sup> The new drama combined the rhetorical complexity of the academic play with the bawdy energy of the moralities. However, it was more ambiguous and complex in its meanings, and less concerned with simple allegory. Inspired by this new style, Shakespeare continued these artistic strategies,<sup class="reference" id="cite_ref-6"><a href="#cite_note-6">[6]</a></sup> creating plays that not only resonated on an emotional level with audiences but also explored and debated the basic elements of what it means to be human. What Marlowe and Kyd did for tragedy, <a href="/wiki/John_Lyly" title="John Lyly">John Lyly</a> and <a href="/wiki/George_Peele" title="George Peele">George Peele</a>, among others, did for comedy: they offered models of witty dialogue, romantic action, and exotic, often pastoral location that formed the basis of Shakespeare's comedic mode throughout his career.<sup class="noprint Inline-Template Template-Fact" style="white-space:nowrap;">[<i><a href="/wiki/Wikipedia:Citation_needed" title="Wikipedia:Citation needed">citation needed</a></i>]</sup></p>
<p>Shakespeare's Elizabethan tragedies (including the history plays with tragic designs, such as <i>Richard II</i>) demonstrate his relative independence from classical models. He takes from Aristotle and <a href="/wiki/Horace" title="Horace">Horace</a> the notion of decorum; with few exceptions, he focuses on high-born characters and national affairs as the subject of tragedy. In most other respects, though, the early tragedies are far closer to the spirit and style of moralities. They are episodic, packed with character and incident; they are loosely unified by a theme or character.<sup class="reference" id="cite_ref-7"><a href="#cite_note-7">[7]</a></sup> In this respect, they reflect clearly the influence of Marlowe, particularly of <i><a class="mw-redirect" href="/wiki/Tamburlaine_(play)" title="Tamburlaine (play)">Tamburlaine</a></i>. Even in his early work, however, Shakespeare generally shows more restraint than Marlowe; he resorts to grandiloquent rhetoric less frequently, and his attitude towards his heroes is more nuanced, and sometimes more sceptical, than Marlowe's.<sup class="reference" id="cite_ref-8"><a href="#cite_note-8">[8]</a></sup> By the turn of the century, the bombast of <i>Titus Andronicus</i> had vanished, replaced by the subtlety of <i>Hamlet</i>.</p>
<p>In comedy, Shakespeare strayed even further from classical models. <i>The Comedy of Errors</i>, an adaptation of <i><a href="/wiki/Menaechmi" title="Menaechmi">Menaechmi</a></i>, follows the model of <a class="mw-redirect" href="/wiki/New_comedy" title="New comedy">new comedy</a> closely. Shakespeare's other Elizabethan comedies are more romantic. Like Lyly, he often makes romantic intrigue (a secondary feature in Latin new comedy) the main plot element;<sup class="reference" id="cite_ref-9"><a href="#cite_note-9">[9]</a></sup> even this romantic plot is sometimes given less attention than witty dialogue, deceit, and jests. The "reform of manners," which Horace considered the main function of comedy,<sup class="reference" id="cite_ref-10"><a href="#cite_note-10">[10]</a></sup> survives in such episodes as the gulling of <a href="/wiki/Malvolio" title="Malvolio">Malvolio</a>.</p>
</div>
    """
)

# roy submitted the content for review
writing_task.status = enums.TaskStatus.FINISHED
set_task_completed_time(writing_task, datetime.date(2016, 02, 17))
writing_task.save()


brief_mockdata = [
    (savy, connverse_media, 'Food and Travel')
]


# for user, organization, title in brief_mockdata:
#     for j in range(0, 10):
#         task_brief = TaskBrief.objects.create(
#             creator=user,
#             organization=organization,
#             title=title,
#             description="I quickly followed suit, and descending into the"
#             "bar-room accosted the grinning landlord very pleasantly. "
#             "I cherished no malice towards him, though he had been "
#             "skylarking with me not a little in the matter of my bedfellow."
#             " "
#             "However, a good laugh is a mighty good thing, and rather too "
#             "scarce a good thing; the more\'s the pity. So, if any one man, "
#             "in his own proper person, afford stuff for a good joke to "
#             "anybody, let him not be backward, but let him cheerfully allow "
#             "himself to spend and be spent in that way. And the man that has "
#             "anything bountifully laughable about him, be sure there is more "
#             "in that man than you perhaps think for.",
#             deadline=timezone.now()
#         )
#         last_task = None
#         for k in range(0, 3):
#             task = Task.objects.create(
#                 task_brief=task_brief, type=enums.TaskType.WRITING,
#                 deadline=timezone.now(),
#                 description="Elon Reeve Musk (June 28, 1971)"
#                 " is a South African-born Canadian-American business magnate,[8][9]"
#                 " engineer,[10] inventor[11] and investor.[12][13][14] He is the CEO"
#                 " and CTO of SpaceX, CEO and product architect of Tesla Motors, and"
#                 " chairman of SolarCity. He is the founder of SpaceX and a co-founder"
#                 " of Zip2, PayPal, and Tesla Motors.[15][16][17] He has also envisioned"
#                 " a conceptual high-speed transportation system known as the Hyperloop"
#                 " and has proposed a VTOL supersonic jet aircraft with electric fan"
#                 " propulsion.[18][19]"
#             )
#             if last_task:
#                 task.set_predecessor(last_task)
#             else:
#                 accept_task = task_brief.accept_task()
#                 task.set_successor(accept_task)
#             last_task = task

#             task_meta = task.writing_meta
#             task_meta.word_count = 100
#             task_meta.type = randint(1, len(enums.WritingContentType.choices()))
#             task_meta.goal = randint(1, len(enums.WritingGoal.choices()))
#             task_meta.style = randint(1, len(enums.WritingStyle.choices()))
#             task_meta.point_of_view = randint(1, len(enums.WritingPointOfView.choices()))
#             task_meta.save()

#             job = Job.objects.create(
#                 task=task, price=100, closing_date=timezone.now(),
#                 description="Steven Paul Jobs (February 24, 1955"
#                 " known as the co-founder, chairman, and chief executive officer "
#                 "(CEO) of Apple Inc.; CEO and largest shareholder of Pixar"
#                 "Animation Studios;[3] a member of The Walt Disney Company's"
#                 "board of directors following its acquisition of Pixar; and"
#                 "founder, chairman, and CEO of NeXT Inc. Jobs is widely recognized"
#                 "as a pioneer of the microcomputer revolution of the 1970s, along"
#                 "with Apple co-founder Steve Wozniak. Shortly after his death,"
#                 "Jobs's official biographer, Walter Isaacson, described him as"
#                 "the \"creative entrepreneur whose passion for perfection and"
#                 "ferocious drive revolutionized six industries: personal computers,"
#                 "animated movies, music, phones, tablet computing, and digital"
#                 "publishing.\"[2]"
#             )

#         if j > 2:
#             task_brief.published = True
#             task_brief.save()


# category_count = Category.objects.all().count()
# job_count = Job.objects.all().count()
# for j in range(0, job_count):
#     job_category_ids = []
#     for k in range(0, randint(1, category_count // 2)):
#         category_id = randint(1, category_count)
#         while (category_id in job_category_ids):
#             category_id = randint(1, category_count)
#         job_category_ids.append(category_id)
#         JobCategory.objects.create(
#             job=Job.objects.get(pk=j+1),
#             category=Category.objects.get(pk=category_id)
#         )


# for j in range(0, 10):
#     User.objects.create_user(
#         username='user%d' % j,
#         email='user%d@boltmedia.co' % j,
#         password='password'
#     )

# ken_application = Application.objects.create(
#     job=Job.objects.get(id=1),
#     applicant=ken,
#     status= # 1,2,3
#     message="I think the best way to address this brief is by focusing on what"
#     " your readers care about: Why whale oil is good for the environment "
#     "and the economy!",
# )
# for j in range(0, 10):
#     Application.objects.create(
#         job=Job.objects.get(id=1),
#         applicant=User.objects.get(id=4+j),
#         message="Please hire me, I need money. I can write well, I promise."
#     )

# tim_application = Application.objects.create(
#     job=Job.objects.get(id=2),
#     applicant=tim,
#     message="i m rly gr3at so dats y ew should hire me yo.",
# )
# for j in range(0, 10):
#     Application.objects.create(
#         job=Job.objects.get(id=2),
#         applicant=User.objects.get(id=4+j),
#         message="Please hire me, I need money. I can write well, I promise."
#     )


# ken_application2 = Application.objects.create(
#     job=Job.objects.get(id=3),
#     applicant=ken,
#     message="Four score and seven years ago our fathers brought forth on this"
#     " continent a new nation, conceived in liberty, and dedicated to the"
#     " proposition that all men are created equal.",
# )
# for j in range(0, 10):
#     Application.objects.create(
#         job=Job.objects.get(id=3),
#         applicant=User.objects.get(id=4+j),
#         message="Please hire me, I need money. I can write well, I promise."
#     )

# for j in range(0, 50):
#     org = Organization.objects.create(
#         name='org%d' % j,
#         website='https://boltmedia.co',
#         description='This is org %d' % j,
#         year_founded=2015,
#         size=j * 10
#     )
#     OrganizationUser.objects.create(
#         user=ken,
#         organization=org,
#         user_role=OrganizationUser.USER_ROLE_OWNER
#     )

# ken_application.status = Application.STATUS_ACCEPTED
# ken_application.save()

# ken_application2.status = Application.STATUS_PENDING
# ken_application2.save()

# tim_application.status = Application.STATUS_REJECTED
# tim_application.save()
