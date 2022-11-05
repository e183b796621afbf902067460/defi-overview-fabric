from web3 import Web3
from web3.exceptions import ContractLogicError

from defi.protocols.ellipsis.contracts.Pool import EllipsisPoolContract
from defi.protocols.ellipsis.tokens.RewardsToken import EllipsisRewardsTokenContract
from defi.protocols.ellipsis.contracts.EllipsisLPStaking import EllipsisLPStakingContract

from head.interfaces.overview.builder import IInstrumentOverview
from head.decorators.threadmethod import threadmethod
from head.bridge.configurator import BridgeConfigurator

from providers.abstracts.fabric import providerAbstractFabric

from overviews.protocols.curve.overview import CurveDEXPoolOverview


class EllipsisDEXPoolOverview(CurveDEXPoolOverview, EllipsisPoolContract):
    pass


class EllipsisFarmingPoolOverview(IInstrumentOverview, EllipsisRewardsTokenContract):
    _chiefContract: EllipsisLPStakingContract = EllipsisLPStakingContract()

    _providers: dict = {
        'bsc': {
            'provider': BridgeConfigurator(
                            abstractFabric=providerAbstractFabric,
                            fabricKey='http',
                            productKey='bsc')\
                            .produceProduct()
        }
    }

    _chiefAddresses: dict = {
        _providers['bsc']['provider']:
            {
                'chief': '0x5B74C99AA2356B4eAa7B85dC486843eDff8Dfdbe'
            }
    }

    @threadmethod
    def getOverview(self, *args, **kwargs) -> list:
        overview: list = list()

        symbol: str = self.symbol()
        decimals: int = self.decimals()
        price: float = self.trader.getPrice(major=symbol, vs='USD')

        totalLPLocked: int = self.balanceOf(address=self._chiefAddresses[self.provider]['chief'])

        aOverview: dict = {
            'symbol': symbol,
            'reserve': totalLPLocked / 10 ** decimals,
            'price': price
            }
        overview.append(aOverview)
        return overview


class EllipsisFarmingPoolAllocationOverview(EllipsisFarmingPoolOverview):
    @threadmethod
    def getOverview(self, address, *args, **kwargs) -> list:
        overview: list = list()

        address: str = Web3.toChecksumAddress(address)
        chief: EllipsisLPStakingContract = self._chiefContract\
                .setAddress(address=self._chiefAddresses[self.provider]['chief'])\
                .setProvider(provider=self.provider)\
                .create()

        amount: int = chief.userInfo(token=self.address, address=address)[0]
        decimals: int = self.decimals()
        symbol: str = self.symbol()
        price: float = self.trader.getPrice(major=symbol, vs='USD')

        allocationOverview: dict = {
            'symbol': symbol,
            'amount': amount / 10 ** decimals,
            'price': price
        }
        overview.append(allocationOverview)
        return overview
