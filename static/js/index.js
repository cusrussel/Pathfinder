function hideContentAgain(){
  document.getElementById('r-result').classList.remove("show");
    document.getElementById('r-content').classList.remove("show");

    const secondaryButtons = document.querySelectorAll('#question-17 .r-buttons button');
  secondaryButtons.forEach(button => {
    button.disabled = false; 
    button.style.opacity = 1; 
  });

    begin();
    resetQuestions();
}

function validateEmail() {
  const emailContainer = document.getElementById('float-email');
  const emailInput = document.getElementById("emailInput").value;

  // Check if the email ends with @gmail.com
  if (!emailInput.endsWith("@gmail.com")) {

    const failedMessage = document.createElement("div");
    failedMessage.textContent = "Enter a valid Gmail Address!";
    failedMessage.style.position = "fixed";
    failedMessage.style.top = "120px";
    failedMessage.style.right = "20px";
    failedMessage.style.backgroundColor = "#f44336"; 
    failedMessage.style.color = "#fff";
    failedMessage.style.padding = "10px";
    failedMessage.style.borderRadius = "5px";
    failedMessage.style.zIndex = "9999";
    document.body.appendChild(failedMessage);

    setTimeout(() => {
      failedMessage.style.display = "none";
    }, 3000);
    
    document.getElementById("emailInput").value = "";
    return false; 
  } else {
    emailContainer.style.display = "none";
    emailContainer.classList.add("hidden");
    emailContainer.classList.remove("show");

    const successMessage = document.createElement("div");
    successMessage.textContent = "Sending...";
    successMessage.style.position = "fixed";
    successMessage.style.top = "120px";
    successMessage.style.right = "20px";
    successMessage.style.backgroundColor = "#4CAF50";
    successMessage.style.color = "#fff";
    successMessage.style.padding = "10px";
    successMessage.style.borderRadius = "5px";
    successMessage.style.zIndex = "9999";
    document.body.appendChild(successMessage);

    setTimeout(() => {
        successMessage.style.display = "none";
    }, 4000);

    setTimeout(() => {
        const success1Message = document.createElement("div");
        success1Message.textContent = "A copy has been sent to your email.";
        success1Message.style.position = "fixed";
        success1Message.style.top = "120px";
        success1Message.style.right = "20px";
        success1Message.style.backgroundColor = "#4CAF50";
        success1Message.style.color = "#fff";
        success1Message.style.padding = "10px";
        success1Message.style.borderRadius = "5px";
        success1Message.style.zIndex = "9999";
        document.body.appendChild(success1Message);

        setTimeout(() => {
            success1Message.style.display = "none";
        }, 2000);
    }, 4000); 

    return true; // Allow form submission
  }
}


function toggleEmail() {
  const emailContainer = document.getElementById('float-email');
  
  if (emailContainer.style.display === "none" || !emailContainer.style.display) {
    emailContainer.style.display = "flex";
    emailContainer.classList.add("show");
    emailContainer.classList.remove("hidden");
  } else {
    emailContainer.style.display = "none";
    emailContainer.classList.add("hidden");
    emailContainer.classList.remove("show");
  }
}

function resetQuestions() {
  currentQuestion = 1;

  const allQuestions = document.querySelectorAll('[id^="question-"]');
  allQuestions.forEach((question) => {
      question.classList.add('hidden');
  });

  const firstQuestion = document.getElementById('question-1');
  if (firstQuestion) {
      firstQuestion.classList.remove('hidden');
  }

  updateNextButtonState();
}

function getFirstPathSegment() {
  const pathSegments = window.location.pathname.split("/").filter(Boolean);
  return pathSegments[0] || null; 
}

document.addEventListener("DOMContentLoaded", function () {
  const firstSegment = getFirstPathSegment();

  if (firstSegment) {
    links.forEach((link) => {
      const anchor = link.querySelector("a");
      if (anchor) {
        const href = new URL(anchor.href).pathname;
        const linkFirstSegment = href.split("/").filter(Boolean)[0];

        if (linkFirstSegment === firstSegment) {
          links.forEach((link) => link.classList.remove("active"));
          link.classList.add("active");
        }
      }
    });
  }
});

const links = document.querySelectorAll(".button-background");

// Check the URL path on page load and set the active link based on it
document.addEventListener("DOMContentLoaded", function () {
  const currentPath = window.location.pathname; 

  links.forEach((link) => {
    const anchor = link.querySelector("a");
    if (anchor) {
      const href = anchor.getAttribute("href");
      if (href === currentPath) {
        links.forEach((link) => link.classList.remove("active"));
        link.classList.add("active");
      }
    }
  });
});

// Update the URL path without setting the 'active' link based on clicks
links.forEach((link) => {
  link.addEventListener("click", function (event) {
    event.preventDefault();

    const anchor = this.querySelector("a");
    const href = anchor.getAttribute("href");

    if (href) {
      window.location.href = href;
    }
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const elements = document.querySelectorAll(".fade-in-up");

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.1,
    }
  );

  elements.forEach((element) => {
    observer.observe(element);
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const elements = document.querySelectorAll(".fade-in-up");

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target); 
        }
      });
    },
    {
      threshold: 0.1, 
    }
  );

  elements.forEach((element) => {
    observer.observe(element);
  });
});


function filterItems() {
  const filter = document.getElementById("program-filter").value;
  const items = document.querySelectorAll(".item");

  items.forEach(item => {
    if (filter === "all") {
        if (item.classList.contains("all")) {
            item.style.removeProperty("display");
        } else {
            item.style.display = "none"; 
        }
    } else {

        if (item.classList.contains(filter)) {
            item.style.removeProperty("display");
        } else {
            item.style.display = "none"; 
        }
    }
});
}

window.addEventListener("load", function () {
  document.querySelectorAll(".h-left-picture").forEach((picture) => {
    picture.classList.add("animate");
  });
  document.querySelectorAll(".h-right-picture").forEach((picture) => {
    picture.classList.add("animate");
  });
});

window.addEventListener("load", function () {
  document.querySelector(".h-content-bot").classList.add("animate");

  document.querySelector("h1").classList.add("animate");
  document.querySelector("p").classList.add("animate");
});

document.addEventListener("DOMContentLoaded", function () {
  const elementsToAnimate = document.querySelectorAll(
    ".htw, .htw-desc-background-1, .htw-desc-background-2, .htw-desc-background-3, .htw-link"
  );

  const options = {
    root: null,
    rootMargin: "0px",
    threshold: 0.1,
  };

  const handleIntersect = (entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("animate");
        observer.unobserve(entry.target); 
      }
    });
  };

  const observer = new IntersectionObserver(handleIntersect, options);

  elementsToAnimate.forEach((element) => {
    observer.observe(element);
  });
});


console.log(sessionStorage.getItem('total_questions'));
let currentQuestion = 0;
// const totalQuestionsElement = document.getElementById('total-questions');
// const totalQuestions = totalQuestionsElement.getAttribute('data-total');

const totalQuestions = 21;

document.addEventListener('DOMContentLoaded', function() {
  var element = document.getElementById('total-questions');
  if (element) {
      var totalQuestions = element.getAttribute('data-total');
      console.log(totalQuestions);
      document.getElementById(`question-${0}`).classList.remove('hidden');
  }
});

const formData = {
  specialized_subj: 13.149,
  strand: 11.105,
  specialization: 11.108,
  core_subj: 11.805,
};


function nextQuestion(event, questionNumber){

    const humssOptions = ['Philippine Politics and Governance', 'Creative Writing / Malikhaing Pagsulat', 'Creative Nonfiction: The Literary Essay', 'Disciplines and Ideas in the Social Sciences', 'Disciplines and Ideas in the Applied Social Sciences', 'Introduction to World Religions and Belief Systems', 'Trends, Networks and Critical Thinking in the 21st Century Culture','Community Engagement, Solidarity and Citizenship'];
    const abmOptions = ['Business Math', 'Fundamentals of Accounting', 'Business Management', 'Applied Economics', 'Organization and Management', 'Business Finance', 'Business Ethics and Social Responsibility', 'Business Marketing', 'Business Enterprise Simulation'];
    const stemOptions = ['Calculus', 'General Physics', 'General Chemistry', 'General Biology', 'Research/Capstone Project'];

    const button = event.target;
    const fieldName = button.getAttribute('data-field');
    const value = button.getAttribute('data-value');

    formData[fieldName] = value;

    console.log(Object.entries(formData));

    document.getElementById(`question-${questionNumber}`).classList.add('hidden');
  
    // Conditional logic to move to the next question
    if (questionNumber === 7) {
      // If the answer is "No", skip question 4
        if (value === 'No') {
            formData['strand'] = 'None'
            currentQuestion = 13; // Skip to question 5, change this number based on the actual next question
        }
    }

    if(questionNumber === 9){
        if(value === 'ABM'){
            currentQuestion = 9;
        }
    }
    if(questionNumber === 10){
        if(abmOptions.includes(value)){
            currentQuestion = 14;
        }
    } 
    if(questionNumber === 9){
        if(value === 'STEM'){
            currentQuestion = 10;
        }
    }

    if(questionNumber === 11){
        if(stemOptions.includes(value)){
            currentQuestion = 14;
        }
    }
    if(questionNumber === 9){
        if(value === 'HUMSS'){
            currentQuestion = 11;
        }
    } 
    if(questionNumber === 12){
        if(humssOptions.includes(value)){
            currentQuestion = 14;
        }
    }

    if(questionNumber === 9){
        if(value === 'TVL Track'){
            currentQuestion = 12;
        }
    }

    if(questionNumber === 13){
        if(value === 'Cookery' || value === 'ICT/CSS'){
            currentQuestion = 14;
        }
    }

    if(questionNumber === 16){
      const secondaryButtons = document.querySelectorAll('#question-17 .r-buttons button');
      secondaryButtons.forEach(button => {
        if (button.getAttribute('data-value') === value) {
          button.disabled = true;
          button.style.opacity = 0.5; // optional visual effect
        }
      });
    }

    currentQuestion++;
    if (currentQuestion <= totalQuestions) {
        document.getElementById(`question-${currentQuestion}`).classList.remove('hidden');
    } else {
        submitForm();
        document.getElementById('r-questions').classList.remove('show');
        document.getElementById('loader-container').style.display="flex";
        document.getElementById('loader-msg').innerText = "Generating your suitable program...";
        setTimeout(function() {
            document.getElementById("loader-container").style.display = "none";
            document.getElementById('r-result').classList.add('show');
        }, 3000);
        document.getElementById(`question-${currentQuestion}`).classList.add('show');
    }
}

const secondaryButtons = document.querySelectorAll('#question-17 .r-buttons button');

function resetButtons() {
  secondaryButtons.forEach(button => {
    button.disabled = false; 
    button.style.opacity = 1; 
  });
}

async function submitForm() {
  console.log("Submitting form data:", formData); 
  
  let personality = '';

    for (let [key, value] of Object.entries(formData)) {
        if (key.includes('state')) {
          personality += String(value); 
        }
    }

    formData['personality'] = personality;

  try {
      const response = await fetch('/predict', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify(formData)
      });

      if (response.ok) {
          const result = await response.json();
          displayPrediction(result);

          const submitResponse = await fetch('/submit', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify(formData)
          });

          if (submitResponse.ok) {
              const submitData = await submitResponse.json();
              console.log('Success:', submitData);
          } else {
              console.error('Error in /submit response:', submitResponse.statusText);
          }
      } else {
          console.error("Error in /predict response:", response.statusText);
      }
  } catch (error) {
      console.error("Error during fetch:", error);
  }
}             

updateButtonState();

let topPrediction, secondPrediction, thirdPrediction;

function one() {
  displaySinglePrediction(topPrediction, document.getElementById('top-one'), document.getElementById('result-image-one'), document.getElementById('result-image-two'), document.getElementById('result-info'));
}

function two() {
  displaySinglePrediction(secondPrediction, document.getElementById('top-two'), document.getElementById('result-image-one'), document.getElementById('result-image-two'), document.getElementById('result-info'));
}

function three() {
  displaySinglePrediction(thirdPrediction, document.getElementById('top-three'), document.getElementById('result-image-one'), document.getElementById('result-image-two'), document.getElementById('result-info'));
}

function displayPrediction(result) {
  let predictions = result.top_3_predictions;  

  let predictionTextElement = document.getElementById('top-one');
  let predictionTopTwo = document.getElementById('top-two');
  let predictionTopThree =document.getElementById('top-three');
  let predictionImageOneElement = document.getElementById('result-image-one');
  let predictionImageTwoElement = document.getElementById('result-image-two');
  let predictionInfoElement = document.getElementById('result-info');
  
    // Prediction mappings
    const predictionsMap = {
        'AB in Communication': {
            text: "AB in Communication",
            imageOne: "../static/images/recommender/program-images/communication.svg",
            imageTwo: "../static/images/recommender/programs/communication-logo.svg",  
            info: "This program explores the principles of effective communication across various media, including verbal, written, and digital forms. Students develop skills in public speaking, media literacy, and critical thinking, preparing them for careers in journalism, public relations, and corporate communications.",
            href: "/programs/communication"
        },
        'AB in Multimedia Arts': {
            text: "AB in Multimedia Arts",
            imageOne: "../static/images/recommender/program-images/multimedia.svg",
            imageTwo: "../static/images/recommender/programs/multimedia-logo.svg", 
            info: "Focusing on the integration of art and technology, this program covers areas like graphic design, animation, and digital storytelling. Students learn to create compelling multimedia content, equipping them for roles in advertising, film, and interactive media.",
            href: "/programs/multimedia-arts"
        },
        'AB in Political Science': {
            text: "AB in Political Science",
            imageOne: "../static/images/recommender/program-images/polsci.svg",
            imageTwo: "../static/images/recommender/programs/polsci-logo.svg", 
            info: "This program examines political systems, theories, and behaviors, emphasizing critical analysis of governmental structures and public policies. Graduates are prepared for careers in law, public policy, international relations, and advocacy.",
            href: "/programs/political-science"
        },
        'BA in Sociology': {
            text: "BA in Sociology",
            imageOne: "../static/images/recommender/program-images/sociology.svg",
            imageTwo: "../static/images/recommender/programs/socio-logo.svg", 
            info: "Students study social behavior, institutions, and cultural norms, focusing on issues such as inequality, identity, and social change. This program prepares graduates for careers in social work, research, and community organizing.",
            href: "/programs/sociology"
        },
        'BS in Accountancy': {
            text: "BS in Accountancy",
            imageOne: "../static/images/recommender/program-images/accountancy.svg",
            imageTwo: "../static/images/recommender/programs/accountancy-logo.svg", 
            info: "This program equips students with knowledge of financial principles, auditing, and tax regulations. Graduates are prepared for careers in accounting, finance, and corporate management, with a strong emphasis on ethical practices.",
            href: "/programs/accountancy"
        },
        'BS in Architecture': {
            text: "BS in Architecture",
            imageOne: "../static/images/recommender/program-images/archi.svg",
            imageTwo: "../static/images/recommender/programs/archi-logo.svg", 
            info: "Focusing on the design and construction of buildings and spaces, this program combines creativity with technical skills. Students learn about architectural theory, design processes, and sustainability, preparing them for careers as architects or urban planners.",
            href: "/programs/architecture"
        },
        'BS in Business Administration': {
            text: "BS in Business Administration",
            imageOne: "../static/images/recommender/program-images/businessAdmin.svg",
            imageTwo: "../static/images/recommender/programs/businessadd-logo.svg",  
            info: "This program provides a comprehensive understanding of business operations, including management, marketing, and finance. Students develop leadership skills and strategic thinking, preparing them for various roles in the corporate world.",
            href: "/programs/business-administration"
        },
        'BS in Business Marketing': {
            text: "BS in Business Marketing",
            imageOne: "../static/images/recommender/program-images/businessMarketing.svg",
            imageTwo: "../static/images/recommender/programs/business-logo.svg", 
            info: "Focusing on market research, consumer behavior, and promotional strategies, this program prepares students for careers in advertising, brand management, and digital marketing. Students learn to analyze market trends and develop effective marketing campaigns.",
            href: "/programs/business-marketing"
        },
        'BS in Civil Engineering': {
            text: "BS in Civil Engineering",
            imageOne: "../static/images/recommender/program-images/civil.svg",
            imageTwo: "../static/images/recommender/programs/civileng-logo.svg",  
            info: "This program covers the design and construction of infrastructure projects, such as bridges, roads, and buildings. Students gain technical expertise in engineering principles and project management, preparing them for roles in construction and urban development.",
            href: "/programs/civil-engineering"
        },
        'BS in Computer Engineering':{
            text: "BS in Computer Engineering", 
            imageOne: "../static/images/recommender/program-images/compeng.svg",
            imageTwo: "../static/images/recommender/programs/compeng-logo.svg",  
            info: " Combining computer science and electrical engineering, this program focuses on the design and development of computer systems and hardware. Graduates are equipped for careers in software development, system design, and embedded systems.",
            href: "/programs/computer-engineering"
        },
        'BS in Computer Science': {
            text: "BS in Computer Science",
            imageOne: "../static/images/recommender/program-images/cs.svg",
            imageTwo: "../static/images/recommender/programs/comsi-logo.svg",  
            info: "This program delves into programming, algorithms, and data structures, emphasizing problem-solving and computational thinking. Graduates are prepared for careers in software engineering, data analysis, and cybersecurity.",
            href: "/programs/computer-science"
        },
        'BS in Criminology': {
            text: "BS in Criminology",
            imageOne: "../static/images/recommender/program-images/criminology.svg",
            imageTwo: "../static/images/recommender/programs/crim-logo.svg",  
            info: " Focusing on the study of crime, criminal behavior, and the justice system, this program prepares students for careers in law enforcement, criminal justice, and forensic science, emphasizing research and analysis of social issues related to crime.",
            href: "/programs/criminology"
        },
        
        'BS in Culinary Arts': {
            text: "BS in Culinary Arts",
            imageOne: "../static/images/recommender/program-images/culinary.svg",
            imageTwo: "../static/images/recommender/programs/culinary-logo.svg",  
            info: "This program combines culinary skills with management principles, teaching students about food preparation, nutrition, and restaurant operations. Graduates are prepared for careers in the culinary industry, including chefs and food service managers.",
            href: "/programs/culinary-arts"
        },
        'BS in Education': {
            text: "BS in Education",
            imageOne: "../static/images/recommender/program-images/educ.svg",
            imageTwo: "../static/images/recommender/programs/education-logo.svg", 
            info: "This program prepares future educators with knowledge of teaching methods, curriculum development, and child psychology. Graduates are equipped to teach in various educational settings and promote student learning and development.",
            href: "/programs/education"
        },
        'BS in Electronics Engineering': {
            text: "BS in Electronics Engineering",
            imageOne: "../static/images/recommender/program-images/electronicseng.svg",
            imageTwo: "../static/images/recommender/programs/elecengineering-logo.svg", 
            info: "Focusing on electronic systems and circuits, this program covers design, development, and testing of electronic devices. Students gain technical skills for careers in telecommunications, automation, and consumer electronics.",
            href: "/programs/electronics-engineering"
        },
        'BS in Entrepreneurship': {
            text: "BS in Entrepreneurship",
            imageOne: "../static/images/recommender/program-images/entrep.svg",
            imageTwo: "../static/images/recommender/programs/entrep-logo.svg", 
            info: "This program emphasizes innovation and business development, teaching students how to launch and manage startups. Graduates are equipped with skills in business planning, marketing, and financial management, fostering entrepreneurial thinking.",
            href: "/programs/entrepreneurship"
        },
        'BS in Hospitality Management': {
            text: "BS in Hospitality Management",
            imageOne: "../static/images/recommender/program-images/hospitalityManagement.svg",
            imageTwo: "../static/images/recommender/programs/hotelmanagement-logo.svg",  
            info: "Students study the hospitality industry, focusing on hotel management, event planning, and customer service. This program prepares graduates for careers in hotels, restaurants, and tourism management, emphasizing operational efficiency and guest satisfaction.",
            href: "/programs/hospitality-management"
        },
        'BS in Information Technology': {
            text: "BS in Information Technology",
            imageOne: "../static/images/recommender/program-images/it.svg",
            imageTwo: "../static/images/recommender/programs/it-logo.svg",  
            info: "This program covers the use of technology in business, focusing on systems analysis, database management, and network security. Graduates are prepared for careers in IT support, systems administration, and cybersecurity.",
            href: "/programs/information-technology"
        },
        'BS in Mathematics': {
            text: "BS in Mathematics",
            imageOne: "../static/images/recommender/program-images/math.svg",
            imageTwo: "../static/images/recommender/programs/math-logo.svg", 
            info: "Focusing on mathematical theories and applications, this program develops analytical and problem-solving skills. Graduates pursue careers in finance, education, and data science, emphasizing quantitative reasoning.",
            href: "/programs/mathematics"
        },
        'BS in Mechanical Engineering': {
            text: "BS in Mechanical Engineering",
            imageOne: "../static/images/recommender/program-images/mecheng.svg",
            imageTwo: "../static/images/recommender/programs/mechanical-logo.svg", 
            info: "This program covers the design and analysis of mechanical systems, emphasizing principles of physics and material science. Graduates are prepared for careers in manufacturing, automotive, and aerospace industries.",
            href: "/programs/mechanical-engineering"
        },
        'BS in Nursing': {
            text: "BS in Nursing",
            imageOne: "../static/images/recommender/program-images/nursing.svg",
            imageTwo: "../static/images/recommender/programs/nursing-logo.svg",
            info: " This program prepares students for a career in healthcare, emphasizing patient care, medical ethics, and clinical practices. Graduates are equipped to take the licensure exam and work in various healthcare settings, providing essential care to patients.",
            href: "/programs/nursing"
        },
        'AB in Psychology': {
            text: "AB in Psychology",
            imageOne: "../static/images/recommender/program-images/psychology.svg",
            imageTwo: "../static/images/recommender/programs/psycho-logo.svg", 
            info: "Focusing on human behavior and mental processes, this program covers topics such as developmental psychology, social behavior, and mental health. Graduates are prepared for careers in counseling, social services, and research.",
            href: "/programs/psychology"
        },
        'BS in Public Administration': {
            text: "BS in Public Administration",
            imageOne: "../static/images/recommender/program-images/publicAdmin.svg",
            imageTwo: "../static/images/recommender/programs/public-logo.svg", 
            info: "This program examines the management of public sector organizations, focusing on policy analysis, budgeting, and public service ethics. Graduates are equipped for careers in government, non-profit organizations, and public policy advocacy.",
            href: "/programs/public-administration"
        },
        'BS in Statistics': {
            text: "BS in Statistics",
            imageOne: "../static/images/recommender/program-images/stats.svg",
            imageTwo: "../static/images/recommender/programs/stats-logo.svg", 
            info: " Students learn statistical theory and methods, focusing on data analysis and interpretation. This program prepares graduates for careers in data science, market research, and public health, emphasizing quantitative analysis.",
            href: "/programs/statistics"
        },
        'BS in Tourism Management': {
            text: "BS in Tourism Management",
            imageOne: "../static/images/recommender/program-images/tourism.svg",
            imageTwo: "../static/images/recommender/programs/tourism-logo.svg",
            info: "This program studies the tourism industry, emphasizing sustainable practices, marketing strategies, and customer service. Graduates are prepared for careers in travel agencies, hotels, and tourism development, focusing on enhancing the visitor experience.",
            href: "/programs/tourism-management"
        },
    };
  
    function updateProgramDetails(predictionCategory) {
      let predictionData = predictionsMap[predictionCategory];
  
      if (predictionData) {
        predictionInfoElement.innerText = predictionData.info;
        formData['href'] = predictionData.href;
        if (predictionData.imageOne && predictionData.imageTwo) {
          predictionImageOneElement.src = predictionData.imageOne;
          predictionImageOneElement.style.display = 'block';
          predictionImageTwoElement.src = predictionData.imageTwo;
          predictionImageTwoElement.style.display = 'block';
        } else {
          predictionImageOneElement.style.display = 'none';
          predictionImageTwoElement.style.display = 'none';
        }
      } else {
        predictionInfoElement.innerText = "No additional information available.";
        predictionImageOneElement.style.display = 'none';
        predictionImageTwoElement.style.display = 'none';
      }
    }
    
    function handleActiveClass(element) {
      predictionTextElement.classList.remove('r-result-programs-active');
      predictionTopTwo.classList.remove('r-result-programs-active');
      predictionTopThree.classList.remove('r-result-programs-active');
      
      element.classList.add('r-result-programs-active');
    }

    if (predictions && predictions.length > 0) {
      let topPrediction = predictions[0]?.category;
      let secondPrediction = predictions[1]?.category;
      let thirdPrediction = predictions[2]?.category;

      formData['output_1'] = predictions[0]?.category;
      formData['output_2'] = predictions[1]?.category;
      formData['output_3'] = predictions[2]?.category;

      predictionTextElement.innerText = predictionsMap[topPrediction]?.text;
      predictionTopTwo.innerText = predictionsMap[secondPrediction]?.text;
      predictionTopThree.innerText = predictionsMap[thirdPrediction]?.text;
  
      updateProgramDetails(topPrediction);
      handleActiveClass(predictionTextElement);

      predictionTopTwo.onclick = () => {
        updateProgramDetails(secondPrediction);
        handleActiveClass(predictionTopTwo); 
      };

      predictionTopThree.onclick = () => {
        updateProgramDetails(thirdPrediction);
        handleActiveClass(predictionTopThree); 
      };

      predictionTextElement.onclick = () => {
        updateProgramDetails(topPrediction);
        handleActiveClass(predictionTextElement); 
      };
    } else {
      predictionTextElement.innerText = "No predictions available";
      predictionInfoElement.innerText = "";
      predictionImageOneElement.style.display = 'none';
      predictionImageTwoElement.style.display = 'none';
    }
}
    document.getElementById('question-1').classList.remove('hidden');

function disableLinksOnResize() {
  if (window.innerWidth <= 1000) {
      document.querySelectorAll('nav a').forEach(link => {
          link.addEventListener('click', function(event) {
              event.preventDefault();
          });
      });
  } else {
      document.querySelectorAll('nav a').forEach(link => {
          link.removeEventListener('click', function(event) {
              event.preventDefault();
          });
      });
  }
}

disableLinksOnResize();

window.addEventListener('resize', disableLinksOnResize);

function hideContent(){ 
  document.getElementById('r-begin').classList.add('show');
}

function cancel(){
  document.getElementById('r-begin').classList.remove("show");
}

function begin(){
  document.getElementById('r-begin').classList.remove("show");
  document.getElementById('r-content').classList.add('hidden');
  document.getElementById('loader-container').style.display="flex";
  document.getElementById('loader-msg').innerText = "Preparing the questions...";
  setTimeout(function() {
    document.getElementById("loader-container").style.display = "none";
    document.getElementById('r-questions').classList.add("show");
}, 3000);
}

function getHref(){
  let updateHref = formData.href;
  window.open(updateHref, '_blank');
}

function getPrediction() {
  fetch('/get-prediction')
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        console.log('Error:', data.error);
      } else {
        console.log('Top 3 Predictions:', data.top_3_predictions);
        
        // Clear previous predictions (if any)
        const predictionContainer = document.getElementById('prediction');
        predictionContainer.innerHTML = '';

        // Display the top 3 predictions with their probabilities
        data.top_3_predictions.forEach(prediction => {
          const predictionElement = document.createElement('p');
          predictionElement.innerText = `${prediction.category}: ${prediction.probability}`;
          predictionContainer.appendChild(predictionElement);
        });
      }
    })
    .catch(error => console.error('Error fetching prediction:', error));
}