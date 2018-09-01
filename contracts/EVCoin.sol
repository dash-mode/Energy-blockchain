pragma solidity ^0.4.22;

contract Owned {
    address public owner;
    address public newOwner;

    event OwnershipTransferred(address indexed _from, address indexed _to);

    constructor() public {
        owner = msg.sender;
    }

    modifier onlyOwner {
        require(msg.sender == owner);
        _;
    }

    function transferOwnership(address _newOwner) public onlyOwner {
        newOwner = _newOwner;
    }
    function acceptOwnership() public {
        require(msg.sender == newOwner);
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
        newOwner = address(0);
    }
}

contract ApproveAndCallFallBack {
    function receiveApproval(address from, uint256 tokens, address token, bytes data) public;
}

contract StandardCoin is Owned{
    mapping (address => mapping (address => uint256)) allowed;
    mapping(address => uint256) StandardCoinBalance;
    string public symbol;
    string public  name;
    uint8 public decimals;
    uint256 public totalSupply;

    event Transfer(address indexed _from, address indexed _to, uint256 _value);
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);

    function totalSupply() public constant returns (uint256) {
        return totalSupply;
    }

    function balanceOf(address _owner) public constant returns (uint256) {
        return StandardCoinBalance[_owner];
    }

    function transfer(address _to, uint256 _value) public returns (bool) {
        if(StandardCoinBalance[msg.sender] >= _value && _value > 0) {
            StandardCoinBalance[msg.sender] -= _value;
            StandardCoinBalance[_to] += _value;
            emit Transfer(msg.sender, _to, _value);            
            return true;
        }
        return false;
    }

    // the one who receives coins calls it
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {
        if(StandardCoinBalance[_from] >= _value && _value > 0 && allowed[_from][msg.sender] >= _value) {
            StandardCoinBalance[_from] -= _value;
            StandardCoinBalance[_to] += _value;
            allowed[_from][msg.sender] -= _value;
            emit Transfer(_from, _to, _value);            
            return true;
        }
        return false;
    }

    // the one who gives away coins calls it
    function approve(address _spender, uint256 _value) public returns (bool success) {
        allowed[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }

    function allowance(address _owner, address _spender) public constant returns (uint256 remaining) {
        return allowed[_owner][_spender];
    }

    function approveAndCall(address _spender, uint _tokens, bytes _data) public returns (bool success) {
        allowed[msg.sender][_spender] = _tokens;
        emit Approval(msg.sender, _spender, _tokens);
        ApproveAndCallFallBack(_spender).receiveApproval(msg.sender, _tokens, this, _data);
        return true;
    }

    function () public payable {
        revert();
    }

    function transferAnyERC20Token(address _tokenAddress, uint _tokens) public onlyOwner returns (bool success) {
        return StandardCoin(_tokenAddress).transfer(owner, _tokens);
    }
}

contract EVCoin is StandardCoin {
    constructor() public {
        name = "EVCoin";
        symbol = "EVC";
        decimals = 18;
        totalSupply = 1e18;
        StandardCoinBalance[msg.sender] = 1e18;
    }
}