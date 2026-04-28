import sqlite3
import os

def insert_projects():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    projects = [
        # --- 3 Upcoming Projects ---
        {
            'title': 'Sunset Ridge Modern Villa',
            'description': 'A stunning modern villa perched on the hillside offering panoramic sunset views. This upcoming project features open-concept living spaces, floor-to-ceiling glass walls, and a seamless blend of indoor and outdoor environments. Designed for the discerning homeowner, the villa will include smart home integration, energy-efficient systems, and a private infinity pool.',
            'main_image': '1.jpg',
            'video_file': None,
            'video_url': 'https://www.youtube.com/watch?v=wlKze3e8vGo',
            'category': 'Upcoming',
            'bedrooms': 4,
            'bathrooms': 3,
            'garage': 2,
            'area_size': '4,200 sq ft',
            'floors': 2,
            'location': 'Sunset Ridge, California'
        },
        {
            'title': 'Oakwood Luxury Bungalow',
            'description': 'Nestled among mature oak trees, this luxury bungalow combines rustic charm with contemporary elegance. The upcoming build will showcase natural stone finishes, vaulted timber ceilings, and expansive wraparound porches. Perfect for families seeking tranquility without sacrificing modern amenities.',
            'main_image': '2.jpg',
            'video_file': None,
            'video_url': 'https://www.youtube.com/watch?v=h-9wNCChDrs',
            'category': 'Upcoming',
            'bedrooms': 3,
            'bathrooms': 2,
            'garage': 2,
            'area_size': '3,100 sq ft',
            'floors': 1,
            'location': 'Oakwood Valley, Texas'
        },
        {
            'title': 'Downtown Urban Townhouse',
            'description': 'A sleek urban townhouse in the heart of the city designed for modern professionals. This upcoming project maximizes vertical living with rooftop terraces, a private home office, and state-of-the-art kitchen appliances. Walking distance to premier dining, shopping, and public transit.',
            'main_image': '3.jpg',
            'video_file': None,
            'video_url': 'https://www.youtube.com/watch?v=HmubC3tXdik',
            'category': 'Upcoming',
            'bedrooms': 3,
            'bathrooms': 3,
            'garage': 1,
            'area_size': '2,400 sq ft',
            'floors': 3,
            'location': 'Midtown District, New York'
        },
        # --- 3 Completed Projects ---
        {
            'title': 'Nakshatra Living Estate',
            'description': 'An exclusive gated estate that redefines luxury living. Completed in record time, this property features imported marble flooring, a private cinema, wine cellar, and landscaped gardens with a koi pond. The Nakshatra Estate stands as a benchmark for premium residential construction.',
            'main_image': '4.jpg',
            'video_file': None,
            'video_url': 'https://www.youtube.com/watch?v=JUil7mVW3RU',
            'category': 'Completed',
            'bedrooms': 5,
            'bathrooms': 5,
            'garage': 3,
            'area_size': '6,500 sq ft',
            'floors': 2,
            'location': 'Nakshatra Hills, Arizona'
        },
        {
            'title': 'Greenfield Heritage Home',
            'description': 'A beautifully restored heritage residence that honors classic architecture while integrating modern comforts. This completed project preserved original brickwork and hardwood floors, adding a contemporary kitchen extension and solar panel array. Winner of the Local Heritage Preservation Award.',
            'main_image': '5.jpg',
            'video_file': None,
            'video_url': 'https://www.youtube.com/watch?v=u4zL3KTUEyM',
            'category': 'Completed',
            'bedrooms': 4,
            'bathrooms': 3,
            'garage': 2,
            'area_size': '3,800 sq ft',
            'floors': 2,
            'location': 'Greenfield Historic District, Massachusetts'
        },
        {
            'title': 'Maple Grove Family Residence',
            'description': 'A warm and inviting family home built around a central great room concept. This completed project features a chef-inspired kitchen, finished basement with recreation room, and a backyard deck perfect for entertaining. Designed with growing families in mind, every inch of space is optimized for comfort and functionality.',
            'main_image': '6.jpg',
            'video_file': None,
            'video_url': None,
            'category': 'Completed',
            'bedrooms': 4,
            'bathrooms': 3,
            'garage': 2,
            'area_size': '3,200 sq ft',
            'floors': 2,
            'location': 'Maple Grove, Minnesota'
        }
    ]

    for project in projects:
        cursor.execute('''
            INSERT INTO projects (
                title, description, main_image, video_file, video_url,
                category, bedrooms, bathrooms, garage, area_size, floors, location
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project['title'],
            project['description'],
            project['main_image'],
            project['video_file'],
            project['video_url'],
            project['category'],
            project['bedrooms'],
            project['bathrooms'],
            project['garage'],
            project['area_size'],
            project['floors'],
            project['location']
        ))
        print(f"Inserted project: {project['title']} ({project['category']})")

    conn.commit()
    conn.close()
    print("\nAll projects inserted successfully!")

if __name__ == '__main__':
    insert_projects()

