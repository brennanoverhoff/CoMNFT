pragma solidity ^0.8.17;

import "node_modules/@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "node_modules/@openzeppelin/contracts/access/Ownable.sol";
import "node_modules/@openzeppelin/contracts/utils/Counters.sol";
import "node_modules/@chainlink/contracts/src/v0.8/ChainlinkClient.sol";

contract CoMNFT is ERC721URIStorage, Ownable, ChainlinkClient {
    using Counters for Counters.Counter;
    Counters.Counter private tokenIds;
    using Chainlink for Chainlink.Request;
    string public canonicalizedSmiles;
    address public oracle;
    bytes32 public jobId;
    uint256 public fee;
    struct requestStruct {
        address minter;
        string smiles;
        string uri;
    }
    mapping (bytes32 => requestStruct) public requestMapping;

    event DataFulfilled(string canonicalizedSmiles);

    constructor(address _oracle, bytes32 _jobId, uint256 _fee, address _link) ERC721("CompositionOfMatterNFT","CoMNFT") {
        if (_link == address(0)) {
            setPublicChainlinkToken();
        } else {
            setChainlinkToken(_link);
        }
        oracle = _oracle;
        jobId = _jobId;
        fee = _fee;
    }

    function requestCanonicalizedSmiles(address minter, string memory smiles, string memory tokenURI) public returns (bytes32 requestId) {
        Chainlink.Request memory request = buildChainlinkRequest(
            jobId,
            address(this),
            this.fulfill.selector
        );

        request.add(
            "get",
            string.concat("https://smiles-validator.onrender.com/validate/",tokenURI)
        );

        request.add("path", "smiles");

        requestId = sendChainlinkRequestTo(oracle, request, fee);
        requestMapping[requestId] = requestStruct(minter,smiles,tokenURI);
        return requestId;
    }

    function fulfill(bytes32 _requestId, string memory _canonicalizedSmiles)
        public
        recordChainlinkFulfillment(_requestId)
    {
        canonicalizedSmiles = _canonicalizedSmiles;
        if (keccak256(abi.encodePacked(_canonicalizedSmiles)) == keccak256(abi.encodePacked(requestMapping[_requestId].smiles))) {
            uint newCoMId = uint256(keccak256(abi.encodePacked(requestMapping[_requestId].smiles)));
            _mint(requestMapping[_requestId].minter,newCoMId);
            _setTokenURI(newCoMId,string.concat("https://ipfs.io/ipfs/",requestMapping[_requestId].uri));
            tokenIds.increment();
            //transferFrom(_ownerOf(newCoMId),requestMapping[_requestId].minter,newCoMId);
        }
        emit DataFulfilled(canonicalizedSmiles);
    }

    function totalSupply() public view returns (uint256) {
        return tokenIds.current();
    }

    function contractURI() public pure returns (string memory) {
        return "https://ipfs.io/ipfs/QmRrmHZffDGtLBvR6YbpTs2AXDqJCZWqTherk5FPxmNF9Z";
    }

    function mintCoM(address minter, string memory smiles, string memory tokenURI) public returns (uint){
        canonicalizedSmiles = "";
        requestCanonicalizedSmiles(minter,smiles,tokenURI);
        return 0;
    }

}