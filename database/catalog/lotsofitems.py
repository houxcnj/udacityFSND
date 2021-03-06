from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import SportCategory, Base, SportingItem, User

engine = create_engine('sqlite:///sportscatalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Create dummy user
User1 = User(name="Xiaocheng Hou", email="houxcnj@gmail.com",
             picture='''http://www.cascadechristian.org/editoruploads/images/Athletics/480px-Soccer_ball_svg.png''')
session.add(User1)
session.commit()
# Insert a sports category record into the db
sportsCategory1 = SportCategory(name="Soccer", userId=1)

session.add(sportsCategory1)
session.commit()

# Insert a Sporting Item record into the db
sportingItem1 = SportingItem(name="Goal Keeping Gloves", userId=1,
                             description="Gloves provides a better grip",
                             sport=sportsCategory1)

session.add(sportingItem1)
session.commit()

sportingItem2 = SportingItem(name="Soccer cleats", userId=1,
                             description="Soccer Cleats are made of rubber",
                             sport=sportsCategory1)

session.add(sportingItem2)
session.commit()

sportingItem3 = SportingItem(name="Shin Guards", userId=1,
                             description="Provides protection to player shins",
                             sport=sportsCategory1)

session.add(sportingItem3)
session.commit()

sportingItem4 = SportingItem(name="Socks", userId=1,
                             description="Socks are usually knee length",
                             sport=sportsCategory1)

session.add(sportingItem4)
session.commit()

sportingItem5 = SportingItem(name="Shorts", userId=1,
                             description="Soccer shorts are  above the knee",
                             sport=sportsCategory1)

session.add(sportingItem5)
session.commit()

sportsCategory2 = SportCategory(name="BaseBall", userId=1)

session.add(sportsCategory2)
session.commit()

sportingItem6 = SportingItem(name="BaseBall Gloves", userId=1,
                             description="Assist  in catching baseballs",
                             sport=sportsCategory2)

session.add(sportingItem6)
session.commit()

sportingItem7 = SportingItem(name="BaseBall Bat", userId=1,
                             description="Small wooded or metal club",
                             sport=sportsCategory2)

session.add(sportingItem7)
session.commit()

sportingItem8 = SportingItem(name="BaseBall ", userId=1,
                             description="Assist players in catching balls",
                             sport=sportsCategory2)

session.add(sportingItem8)
session.commit()

sportingItem9 = SportingItem(name="BaseBall Helmet", userId=1,
                             description="A protective head gear",
                             sport=sportsCategory2)

session.add(sportingItem9)
session.commit()

sportingItem10 = SportingItem(name="Bat Bag", userId=1,
                              description="Item used to house baseball bats",
                              sport=sportsCategory2)

session.add(sportingItem10)
session.commit()

sportsCategory3 = SportCategory(name="Snowboarding", userId=1)

session.add(sportsCategory3)
session.commit()

sportingItem11 = SportingItem(name="Goggles", userId=1,
                             description="A protective eye gear",
                             sport=sportsCategory3)

session.add(sportingItem11)
session.commit()

sportingItem12 = SportingItem(name="Snowboard", userId=1,
                             description="Best for any terrain and conditions.",
                             sport=sportsCategory3)

session.add(sportingItem12)
session.commit()

sportsCategory4 = SportCategory(name="Swimming", userId=1)

session.add(sportsCategory4)
session.commit()

sportingItem13 = SportingItem(name="Goggles", userId=1,
                             description="A protective eye gear",
                             sport=sportsCategory4)

session.add(sportingItem13)
session.commit()

sportingItem14 = SportingItem(name="Swimwear", userId=1,
                             description="Best for swim..",
                             sport=sportsCategory4)

session.add(sportingItem14)
session.commit()


print "added menu items!"