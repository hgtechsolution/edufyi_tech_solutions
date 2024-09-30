<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>EdTech Home</title>
    <link rel="shortcut icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">

    <!-- Custom CSS -->
    <style>
        body, html {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f4f7fc;
            color: #333;
        }

        /* Fixed Navbar */
        .navbar {
            background: linear-gradient(45deg, #038ba3, #00d4ff);
            padding: 20px 30px;
            position: fixed;
            top: 0;
            width: 100%;
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .navbar .logo img {
            width: 40px;
            height: 40px;
            margin-right: 10px;
            border-radius: 100px;
        }

        .navbar ul {
            list-style: none;
            display: flex;
            gap: 20px;
        }

        .navbar ul li a {
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 30px;
        }

        .navbar ul li a:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }

        /* Landing Page with Video */
        .hero {
            position: relative;
            height: 100vh;
            background: black;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .hero video {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: 0;
        }

        .hero::after {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6); /* Dark overlay */
            z-index: 1;
        }

        .hero-content {
            position: relative;
            z-index: 2;
            color: white;
            text-align: center;
        }

        .hero-content h1 {
            font-size: 48px;
            margin-bottom: 20px;
        }

        .hero-content p {
            font-size: 20px;
            margin-bottom: 30px;
        }

        .hero-content .btn {
            padding: 10px 20px;
            background-color: #00d4ff;
            color: white;
            border: none;
            border-radius: 30px;
            font-size: 16px;
            cursor: pointer;
        }

        /* About Us Section */
        .about {
            padding: 80px 0;
            text-align: center;
            background: #f9f9f9;
        }

        .about h2 {
            font-size: 36px;
            color: #038ba3;
        }

        .about p {
            font-size: 18px;
            margin: 20px 0;
            color: #555;
        }

        /* Team Section */
        .team {
            padding: 80px 0;
            text-align: center;
            background-color: #fff;
        }

        .team h2 {
            font-size: 36px;
            color: #038ba3;
        }

        .team-cards {
            display: flex;
            justify-content: space-around;
            gap: 20px;
            flex-wrap: wrap;
        }

        .team-card {
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
            width: 300px;
            text-align: center;
        }

        .team-card img {
            border-radius: 50%;
            width: 100px;
            height: 100px;
            margin-bottom: 20px;
        }

        /* Contact Form */
        .contact {
            padding: 80px 0;
            background: #f9f9f9;
            text-align: center;
        }

        .contact h2 {
            font-size: 36px;
            color: #038ba3;
        }

        .contact-form {
            max-width: 600px;
            margin: 0 auto;
        }

        .contact-form input, .contact-form textarea {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            border: 1px solid #ddd;
        }

        .contact-form button {
            padding: 10px 20px;
            background-color: #00d4ff;
            color: white;
            border: none;
            border-radius: 30px;
            font-size: 16px;
            cursor: pointer;
        }

        /* Fixed Footer */
        .footer {
            background-color: #333;
            color: #fff;
            padding: 40px 20px;
            position: fixed;
            bottom: 0;
            width: 100%;
            text-align: center;
        }
    </style>
</head>
<body>

    <!-- Navbar -->
    <nav class="navbar">
        <div class="logo">
            <img src="{{ url_for('static', filename='images/logo.jpg') }}" alt="Logo"> EDUFYI TECH SOLUTIONS
        </div>
        <ul>
            <li><a href="#home">Home</a></li>
            <li><a href="#about">About</a></li>
            <li><a href="#courses">Courses</a></li>
            <li><a href="#team">Team</a></li>
            <li><a href="#contact">Contact</a></li>
        </ul>
    </nav>

    <!-- Landing Video Section -->
    <div class="hero">
        <video autoplay muted loop>
            <source src="{{ url_for('static', filename='videos/landing-video.mp4') }}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <div class="hero-content">
            <h1>Welcome to Edufyi Tech Solutions</h1>
            <p>Your journey to success starts here</p>
            <button class="btn">Start Learning</button>
        </div>
    </div>

    <!-- About Us Section -->
    <section class="about" id="about">
        <h2>About Us</h2>
        <p>We provide top-quality online courses to help you achieve your career goals. Join our community of learners today.</p>
    </section>

    <!-- Team Section -->
    <section class="team" id="team">
        <h2>Meet Our Team</h2>
        <div class="team-cards">
            <div class="team-card">
                <img src="{{ url_for('static', filename='images/team1.jpg') }}" alt="Team Member">
                <h3>John Doe</h3>
                <p>CEO & Founder</p>
            </div>
            <div class="team-card">
                <img src="{{ url_for('static', filename='images/team2.jpg') }}" alt="Team Member">
                <h3>Jane Smith</h3>
                <p>Lead Instructor</p>
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section class="contact" id="contact">
        <h2>Contact Us</h2>
        <form class="contact-form">
            <input type="text" placeholder="Your Name" required>
            <input type="email" placeholder="Your Email" required>
            <textarea placeholder="Your Message" rows="5" required></textarea>
            <button type="submit">Send Message</button>
        </form>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <p>&copy; 2024 Edufyi Tech Solutions. All rights reserved.</p>
    </footer>

</body>
</html>




# Search bar code

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Course For Images</title>
    <style>
        .container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
        }

        .card {
            border: 1px solid #ddd;
            padding: 10px;
            margin: 10px;
            text-align: center;
        }

        img {
            max-width: 300px;
            height: auto;
        }

        .search-bar {
            text-align: center;
            margin-bottom: 20px;
        }

        input[type="text"] {
            padding: 5px;
            width: 200px;
            font-size: 16px;
        }

        button[type="submit"] {
            padding: 5px 10px;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="search-bar">
        <form method="GET" action="{{ url_for('dashboard_courses') }}">
            <input type="text" name="search" placeholder="Search for courses" value="{{ request.args.get('search', '') }}">
            <button type="submit">Search</button>
        </form>
    </div>

    <div class="container">
        {% for image in images %}
        <div class="card">
            <a href="{{ url_for('enroll_course_page', course_name=image.title) }}">
                <img src="{{ image.url }}" alt="{{ image.title }}">
                <p>{{ image.title }}</p>
            </a>
        </div>
        {% endfor %}
    </div>
</body>
</html>
course.html