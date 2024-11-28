
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
    if (questionNumber === '7') {
      // If the answer is "No", skip question 4
        if (value === 'Yes') {
            formData['strand'] = 'None'
            currentQuestion = 12; // Skip to question 5, change this number based on the actual next question
        }
    }

    if(questionNumber === '8'){
        if(value === 'ABM'){
            currentQuestion = 8;
        }
    }
    if(questionNumber === '9'){
        if(abmOptions.includes(value)){
            currentQuestion = 13;
        }
    } 
    if(questionNumber === '8'){
        if(value === 'STEM'){
            currentQuestion = 9;
        }
    }

    if(questionNumber === '10'){
        if(stemOptions.includes(value)){
            currentQuestion = 13;
        }
    }
    if(questionNumber === '8'){
        if(value === 'HUMSS'){
            currentQuestion = 10;
        }
    } 
    if(questionNumber === '11'){
        if(humssOptions.includes(value)){
            currentQuestion = 13;
        }
    }

    if(questionNumber === '8'){
        if(value === 'TVL'){
            currentQuestion = 11;
        }
    }

    if(questionNumber === '12'){
        if(value === 'Cookery' || value === 'ICT/CSS'){
            currentQuestion = 13;
        }
    }

    if(questionNumber === '15'){
      const secondaryButtons = document.querySelectorAll('#question-16 .r-buttons button');
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

updateButtonState();

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