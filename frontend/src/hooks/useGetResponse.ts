import { useState } from "react"
import toast from "react-hot-toast";

const useGetResponse = () => {
    const [loading, setLoading] = useState(false);
    const apiUrl = import.meta.env.VITE_ML_URL;

    const getResponse = async (message: string) => {
        setLoading(true);
        try {
            const res = await fetch(`${apiUrl}/chat`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("FGPT-token")}`
                },
                body: JSON.stringify({message})
            });
            const data = await res.json();

            if (data.error) {
                throw new Error(data.error)
            }

            if (data) {
                return data;
            }
        } catch (error) {
            if (error instanceof Error) {
                toast.error(error.message);
                console.log(error);
            } else {
                console.log("An unknown error occurred", error);
            }
        } finally {
            setLoading(false);
        }
    }

    return { loading, getResponse }
}

export default useGetResponse;