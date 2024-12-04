from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from threading import Lock
import hashlib
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

class VoteRequest(BaseModel):
    voter_id: str
    party_name: str


class BlockchainVotingSystem:
    def __init__(self):
        self.chain = []
        self.current_votes = []
        self.voted_voters = set()
        self.political_parties = [
            "Bharatiya Janata Party (BJP)",
            "Indian National Congress (INC)",
            "Aam Aadmi Party (AAP)",
            "Trinamool Congress (TMC)",
            "Bahujan Samaj Party (BSP)",
            "Samajwadi Party (SP)",
            "Communist Party of India (Marxist) [CPI(M)]",
            "Nationalist Congress Party (NCP)"
        ]
        self.lock = Lock()

    def create_block(self, votes):
        block = {
            'timestamp': datetime.now().isoformat(),
            'votes': votes,
            'previous_hash': self.get_last_block_hash(),
            'block_hash': ''
        }
        block['block_hash'] = self.hash_block(block)
        return block

    def hash_block(self, block):
        block_copy = block.copy()
        block_copy.pop('block_hash', None)
        block_string = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def get_last_block_hash(self):
        return self.chain[-1]['block_hash'] if self.chain else '0'

    def cast_vote(self, voter_id, party_name):
        with self.lock:
            if party_name not in self.political_parties:
                raise HTTPException(status_code=400, detail="Invalid party")

            hashed_voter_id = hashlib.sha256(voter_id.encode()).hexdigest()
            if hashed_voter_id in self.voted_voters:
                raise HTTPException(status_code=400, detail="Voter has already cast a vote")

            vote = {
                'voter_id': hashed_voter_id,
                'party': party_name,
                'timestamp': datetime.now().isoformat()
            }

            self.current_votes.append(vote)
            self.voted_voters.add(hashed_voter_id)

            if len(self.current_votes) >= 10:
                new_block = self.create_block(self.current_votes)
                self.chain.append(new_block)
                self.current_votes = []
                logger.info(f"New block created: {new_block}")

            return {"status": "success", "message": "Vote recorded successfully"}

    def get_election_results(self):
        with self.lock:
            results = {}
            for block in self.chain:
                for vote in block['votes']:
                    results[vote['party']] = results.get(vote['party'], 0) + 1

            for vote in self.current_votes:
                results[vote['party']] = results.get(vote['party'], 0) + 1

            return results

voting_system = BlockchainVotingSystem()


@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/vote")
async def cast_vote(vote_request: VoteRequest):
    return voting_system.cast_vote(
        vote_request.voter_id,
        vote_request.party_name
    )


@app.get("/results", response_class=HTMLResponse)
async def get_results(request: Request):
    results = voting_system.get_election_results()
    return templates.TemplateResponse("results.html", {"request": request, "results": results})