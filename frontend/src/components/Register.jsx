import { useState } from "react";
import { useNavigate } from "react-router-dom";


function Register(){


    const navigate = useNavigate();


    const [email,setEmail] = useState("");

    const [password,setPassword] = useState("");



    async function register(){

    const response = await fetch(
        "http://localhost:8000/register",
        {
            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                email,
                password
            })
        }
    );


    const data = await response.json();


    console.log("Status :", response.status);
    console.log("Réponse API :", data);



    if(response.status === 200){

        alert("Compte créé avec succès");

        navigate("/");

    }
    else{

        alert(data.detail);

    }

}



    return(


        <div className="login-page">


            <header className="top-header">

                <h1>
                    Secure IoT Platform
                </h1>

            </header>




            <div className="login-card">


                <h2>
                    Inscription
                </h2>



                <input

                    type="email"

                    placeholder="Email"

                    value={email}

                    onChange={
                        e=>setEmail(e.target.value)
                    }

                />



                <input

                    type="password"

                    placeholder="Mot de passe"

                    value={password}

                    onChange={
                        e=>setPassword(e.target.value)
                    }

                />



                <button onClick={register}>

                    Créer un compte

                </button>



                <button

                    className="register-button"

                    onClick={()=>navigate("/")}

                >

                    Retour connexion

                </button>



            </div>



        </div>


    );


}


export default Register;