from fastapi import FastAPI
import aircraft_search

app = FastAPI()


@app.get("/")
def hi():
    return {"success": True, "message": "Hi! Send a request to /query with the \"regno\" parameter",
            "example": "/query?regno=N145DQ",
            "example_with_most_possible_hostname": "http://127.0.0.1:8000/query?regno=N145DQ"}


@app.get("/query")
@app.post("/query")
def query_reg_no(regno: str = None):
    if regno is not None or not bool(regno):
        output = aircraft_search.aircraft_details_query(regno,
                                                        # logging=True
                                                        )
        return output
    else:
        return {"success": False, "message": "Aircraft registration number must not be blank"}
